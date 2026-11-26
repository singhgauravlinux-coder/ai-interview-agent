from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import InterviewSession, InterviewQuestion, ConversationTurn, Evaluation
from app.agents.interviewer import generate_questions, evaluate_answer

def create_interview(db: Session, payload):
    session = InterviewSession(**payload.model_dump(), status="created")
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def start_interview(db: Session, session_id):
    """
    Start an interview exactly once.

    PostgreSQL row-level locking serializes concurrent start requests for the
    same session. If questions already exist, return them instead of inserting
    a second set (for example, when the browser retries a timed-out request).
    """
    from sqlalchemy.exc import IntegrityError

    # Lock the parent row before checking or creating its questions. A second
    # request for this session waits here, then observes the first request's
    # committed status and questions.
    s = (
        db.query(InterviewSession)
        .filter(InterviewSession.id == session_id)
        .with_for_update()
        .populate_existing()
        .one_or_none()
    )
    if not s:
        raise HTTPException(404, "Interview not found")

    if s.status in ("completed", "abandoned"):
        raise HTTPException(409, f"Cannot start interview in state {s.status}")

    existing_questions = (
        db.query(InterviewQuestion)
        .filter(InterviewQuestion.session_id == s.id)
        .order_by(InterviewQuestion.sequence)
        .all()
    )

    # Idempotent retry path: never generate or insert a second question set.
    if existing_questions:
        if s.status in ("created", "ready"):
            s.status = "in_progress"
            if s.started_at is None:
                s.started_at = datetime.now(timezone.utc)
            db.commit()
        elif s.status != "in_progress":
            raise HTTPException(409, f"Cannot start interview in state {s.status}")

        db.expire(s, ["questions"])
        return s

    if s.status not in ("created", "ready"):
        raise HTTPException(409, f"Cannot start interview in state {s.status}")

    try:
        questions = generate_questions(
            s.category, s.job_title, s.skills, s.experience_level
        )
        if not questions:
            raise HTTPException(503, "No interview questions could be generated")

        for i, q in enumerate(questions, start=1):
            db.add(
                InterviewQuestion(
                    session_id=s.id,
                    sequence=i,
                    question=q["question"],
                    competency=q["competency"],
                    difficulty=q.get("difficulty", "medium"),
                    expected_evidence=q.get("expected_evidence", []),
                )
            )

        s.status = "in_progress"
        s.started_at = datetime.now(timezone.utc)
        db.commit()
        db.expire(s, ["questions"])
        return s
    except IntegrityError:
        db.rollback()

        # Defensive recovery for an unexpected competing writer. Do not
        # remove the database uniqueness constraint.
        recovered = db.get(InterviewSession, session_id)
        if recovered:
            recovered_questions = (
                db.query(InterviewQuestion)
                .filter(InterviewQuestion.session_id == session_id)
                .order_by(InterviewQuestion.sequence)
                .all()
            )
            if recovered_questions and recovered.status == "in_progress":
                db.expire(recovered, ["questions"])
                return recovered

        raise HTTPException(
            409,
            "Interview start conflicted with another request. Please retry."
        )
    except Exception:
        db.rollback()
        raise

def submit_answer(db: Session, session_id, question_id, answer: str):
    s = db.get(InterviewSession, session_id)
    if not s or s.status != "in_progress":
        raise HTTPException(409, "Interview is not in progress")
    q = db.get(InterviewQuestion, question_id)
    if not q or q.session_id != s.id:
        raise HTTPException(404, "Question not found for this interview")
    existing = db.query(ConversationTurn).filter_by(session_id=s.id).count()
    db.add(ConversationTurn(session_id=s.id, question_id=q.id, speaker="candidate", content=answer, sequence=existing+1))
    db.commit()
    evaluation = evaluate_answer(q.question, answer, q.competency)
    # Persist evaluation evidence in a separate interviewer/evaluation turn for this starter.
    db.add(ConversationTurn(session_id=s.id, question_id=q.id, speaker="system",
        content=json_safe(evaluation), sequence=existing+2))
    db.commit()
    answered_ids = {str(t.question_id) for t in db.query(ConversationTurn).filter_by(session_id=s.id, speaker="candidate").all() if t.question_id}
    next_q = next((item for item in s.questions if str(item.id) not in answered_ids), None)
    return {"evaluation": evaluation, "next_question": question_payload(next_q) if next_q else None}

def question_payload(q):
    if not q: return None
    return {"id": str(q.id), "sequence": q.sequence, "question": q.question, "competency": q.competency, "difficulty": q.difficulty}

def json_safe(obj):
    import json
    return json.dumps(obj)

def complete_interview(db: Session, session_id):
    s = db.get(InterviewSession, session_id)
    if not s:
        raise HTTPException(404, "Interview not found")
    if s.status not in ("in_progress", "abandoned"):
        raise HTTPException(409, f"Cannot complete interview in state {s.status}")
    turns = [t for t in s.turns if t.speaker == "system"]
    scores = []
    strengths, gaps = [], []
    for t in turns:
        import json
        try:
            e = json.loads(t.content)
            scores.append(e.get("score", 3))
            strengths += e.get("strengths", [])
            gaps += e.get("gaps", [])
        except Exception:
            pass
    report = {
      "summary": "Interview completed. Review the evidence and limitations below.",
      "overall_score": round(sum(scores)/len(scores)*20, 1) if scores else None,
      "score_scale": "0-100, derived from mean 1-5 answer scores",
      "strengths": list(dict.fromkeys(strengths)),
      "improvement_areas": list(dict.fromkeys(gaps)),
      "answer_evaluations": [t.content for t in turns],
      "human_review_required": True,
      "limitations": "Scores are preliminary model-assisted indicators, not validated hiring decisions. Review transcripts and evidence."
    }
    s.status = "completed"
    s.completed_at = datetime.now(timezone.utc)
    ev = db.query(Evaluation).filter_by(session_id=s.id).one_or_none()
    if ev:
        ev.overall_score = report["overall_score"]; ev.report = report
    else:
        db.add(Evaluation(session_id=s.id, overall_score=report["overall_score"], coverage=len(scores)/max(1,len(s.questions)), report=report))
    db.commit()
    return report
