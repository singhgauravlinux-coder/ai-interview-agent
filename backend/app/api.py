from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import InterviewCreate, AnswerCreate
from app import services
from app.models import InterviewSession, Evaluation, ConversationTurn

router = APIRouter()

@router.post("/interviews")
def create(payload: InterviewCreate, db: Session = Depends(get_db)):
    s = services.create_interview(db, payload)
    return {"id": str(s.id), "status": s.status, "job_title": s.job_title}

@router.get("/interviews")
def list_interviews(db: Session = Depends(get_db)):
    rows = db.query(InterviewSession).order_by(InterviewSession.created_at.desc()).limit(100).all()
    return [{"id":str(s.id),"job_title":s.job_title,"category":s.category,"status":s.status,"mode":s.mode} for s in rows]

@router.get("/interviews/{session_id}")
def get_interview(session_id: UUID, db: Session = Depends(get_db)):
    s = db.get(InterviewSession, session_id)
    if not s: raise HTTPException(404, "Interview not found")
    answered = db.query(ConversationTurn).filter_by(session_id=s.id, speaker="candidate").all()
    answered_ids = list({str(turn.question_id) for turn in answered if turn.question_id})
    return {"id":str(s.id),"status":s.status,"job_title":s.job_title,"category":s.category,
            "duration_minutes":s.duration_minutes,"questions":[services.question_payload(q) for q in s.questions],
            "answered_question_ids": answered_ids}

@router.post("/interviews/{session_id}/start")
def start(session_id: UUID, db: Session = Depends(get_db)):
    s = services.start_interview(db, session_id)
    first = s.questions[0] if s.questions else None
    return {"session_id":str(s.id),"status":s.status,"first_question":services.question_payload(first)}

@router.post("/interviews/{session_id}/answer")
def answer(session_id: UUID, payload: AnswerCreate, db: Session = Depends(get_db)):
    return services.submit_answer(db, session_id, payload.question_id, payload.answer)

@router.post("/interviews/{session_id}/complete")
def complete(session_id: UUID, db: Session = Depends(get_db)):
    return services.complete_interview(db, session_id)

@router.get("/interviews/{session_id}/report")
def report(session_id: UUID, db: Session = Depends(get_db)):
    ev = db.query(Evaluation).filter_by(session_id=session_id).one_or_none()
    if not ev: raise HTTPException(404, "Report not available; complete the interview first")
    return ev.report
