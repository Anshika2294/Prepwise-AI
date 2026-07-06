from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ── Auth ──
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

# ── Resume ──
class ResumeOut(BaseModel):
    id: int
    ats_score: float
    parsed_text: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

# ── Interview ──
class SessionCreate(BaseModel):
    job_role: str

class SessionOut(BaseModel):
    id: int
    job_role: str
    started_at: datetime

    class Config:
        from_attributes = True

class AnswerSubmit(BaseModel):
    question_id: int
    user_answer: str

class QuestionOut(BaseModel):
    id: int
    question_text: str
    keyword_score: Optional[float]
    grammar_score: Optional[float]
    relevance_score: Optional[float]
    ai_feedback: Optional[str]

    class Config:
        from_attributes = True