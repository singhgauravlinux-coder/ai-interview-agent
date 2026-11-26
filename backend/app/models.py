import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, Float, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mode: Mapped[str] = mapped_column(String(20))
    category: Mapped[str] = mapped_column(String(30))
    interaction_mode: Mapped[str] = mapped_column(String(20))
    job_title: Mapped[str] = mapped_column(String(200))
    experience_level: Mapped[str] = mapped_column(String(30))
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30)
    status: Mapped[str] = mapped_column(String(30), default="created")
    skills: Mapped[list] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    questions: Mapped[list["InterviewQuestion"]] = relationship(back_populates="session", cascade="all, delete-orphan", order_by="InterviewQuestion.sequence")
    turns: Mapped[list["ConversationTurn"]] = relationship(back_populates="session", cascade="all, delete-orphan", order_by="ConversationTurn.sequence")

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("interview_sessions.id", ondelete="CASCADE"))
    sequence: Mapped[int] = mapped_column(Integer)
    question: Mapped[str] = mapped_column(Text)
    competency: Mapped[str] = mapped_column(String(150))
    difficulty: Mapped[str] = mapped_column(String(20))
    expected_evidence: Mapped[list] = mapped_column(JSONB, default=list)
    session: Mapped["InterviewSession"] = relationship(back_populates="questions")
    __table_args__ = (UniqueConstraint("session_id", "sequence"),)

class ConversationTurn(Base):
    __tablename__ = "conversation_turns"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("interview_sessions.id", ondelete="CASCADE"))
    question_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("interview_questions.id", ondelete="SET NULL"), nullable=True)
    speaker: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    sequence: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    session: Mapped["InterviewSession"] = relationship(back_populates="turns")
    __table_args__ = (UniqueConstraint("session_id", "sequence"),)

class Evaluation(Base):
    __tablename__ = "evaluations"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("interview_sessions.id", ondelete="CASCADE"), unique=True)
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    coverage: Mapped[float] = mapped_column(Float, default=0)
    report: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
