from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID
from datetime import datetime

class InterviewCreate(BaseModel):
    mode: Literal["recruitment", "practice"] = "practice"
    category: Literal["technical", "hr", "managerial", "mixed"] = "technical"
    interaction_mode: Literal["text", "voice"] = "text"
    job_title: str = Field(min_length=2, max_length=200)
    experience_level: Literal["entry", "junior", "mid", "senior", "lead"] = "mid"
    duration_minutes: int = Field(default=30, ge=10, le=120)
    skills: list[str] = Field(default_factory=list, max_length=30)

class AnswerCreate(BaseModel):
    question_id: UUID
    answer: str = Field(min_length=1, max_length=12000)

class QuestionOut(BaseModel):
    id: UUID
    sequence: int
    question: str
    competency: str
    difficulty: str

class InterviewOut(BaseModel):
    id: UUID
    mode: str
    category: str
    interaction_mode: str
    job_title: str
    status: str
    duration_minutes: int
    created_at: datetime
    class Config:
        from_attributes = True
