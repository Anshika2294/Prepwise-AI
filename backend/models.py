from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String(100))
    email        = Column(String(100), unique=True, index=True)
    password     = Column(String(255))
    created_at   = Column(DateTime, default=datetime.utcnow)

    resumes      = relationship("Resume", back_populates="user")
    sessions     = relationship("InterviewSession", back_populates="user")


class Resume(Base):
    __tablename__ = "resumes"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"))
    file_path    = Column(String(255))
    ats_score    = Column(Float, default=0.0)
    parsed_text  = Column(Text)
    uploaded_at  = Column(DateTime, default=datetime.utcnow)

    user         = relationship("User", back_populates="resumes")


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"))
    job_role     = Column(String(100))
    started_at   = Column(DateTime, default=datetime.utcnow)
    ended_at     = Column(DateTime, nullable=True)

    user         = relationship("User", back_populates="sessions")
    questions    = relationship("InterviewQuestion", back_populates="session")


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id              = Column(Integer, primary_key=True, index=True)
    session_id      = Column(Integer, ForeignKey("interview_sessions.id"))
    question_text   = Column(Text)
    user_answer     = Column(Text, nullable=True)
    keyword_score   = Column(Float, default=0.0)
    grammar_score   = Column(Float, default=0.0)
    relevance_score = Column(Float, default=0.0)
    ai_feedback     = Column(Text, nullable=True)

    session         = relationship("InterviewSession", back_populates="questions")