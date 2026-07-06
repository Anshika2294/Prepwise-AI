import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from database import get_db
from models import InterviewSession, InterviewQuestion, Resume, User
from utils.jwt_handler import verify_token

router = APIRouter(prefix="/report", tags=["Report"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ── Current user helper ──
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ── 1. Dashboard — saari sessions ka summary ──
@router.get("/dashboard")
def get_dashboard(
    db: Session  = Depends(get_db),
    current_user = Depends(get_current_user)
):
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id
    ).all()

    if not sessions:
        return {"message": "No sessions found", "data": []}

    result = []

    for session in sessions:
        questions = db.query(InterviewQuestion).filter(
            InterviewQuestion.session_id == session.id
        ).all()

        answered = [q for q in questions if q.user_answer]

        if answered:
            avg_keyword   = round(sum(q.keyword_score   or 0 for q in answered) / len(answered), 2)
            avg_grammar   = round(sum(q.grammar_score   or 0 for q in answered) / len(answered), 2)
            avg_relevance = round(sum(q.relevance_score or 0 for q in answered) / len(answered), 2)
            overall       = round((avg_keyword + avg_grammar + avg_relevance) / 3, 2)
        else:
            avg_keyword = avg_grammar = avg_relevance = overall = 0.0

        result.append({
            "session_id"      : session.id,
            "job_role"        : session.job_role,
            "date"            : session.started_at,
            "total_questions" : len(questions),
            "answered"        : len(answered),
            "avg_keyword"     : avg_keyword,
            "avg_grammar"     : avg_grammar,
            "avg_relevance"   : avg_relevance,
            "overall_score"   : overall,
        })

    return {"user": current_user.name, "sessions": result}


# ── 2. Single session ka detail report ──
@router.get("/session/{session_id}")
def get_session_report(
    session_id: int,
    db: Session  = Depends(get_db),
    current_user = Depends(get_current_user)
):
    session = db.query(InterviewSession).filter(
        InterviewSession.id      == session_id,
        InterviewSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    questions = db.query(InterviewQuestion).filter(
        InterviewQuestion.session_id == session_id
    ).all()

    answered = [q for q in questions if q.user_answer]

    if answered:
        avg_keyword   = round(sum(q.keyword_score   or 0 for q in answered) / len(answered), 2)
        avg_grammar   = round(sum(q.grammar_score   or 0 for q in answered) / len(answered), 2)
        avg_relevance = round(sum(q.relevance_score or 0 for q in answered) / len(answered), 2)
        overall       = round((avg_keyword + avg_grammar + avg_relevance) / 3, 2)
    else:
        avg_keyword = avg_grammar = avg_relevance = overall = 0.0

    return {
        "session_id"   : session.id,
        "job_role"     : session.job_role,
        "started_at"   : session.started_at,
        "ended_at"     : session.ended_at,
        "overall_score": overall,
        "avg_keyword"  : avg_keyword,
        "avg_grammar"  : avg_grammar,
        "avg_relevance": avg_relevance,
        "questions": [
            {
                "q_no"           : i + 1,
                "question"       : q.question_text,
                "answer"         : q.user_answer or "Not answered",
                "keyword_score"  : q.keyword_score  or 0,
                "grammar_score"  : q.grammar_score  or 0,
                "relevance_score": q.relevance_score or 0,
                "feedback"       : q.ai_feedback    or "No feedback",
            }
            for i, q in enumerate(questions)
        ]
    }


# ── 3. ATS Score history ──
@router.get("/ats-history")
def get_ats_history(
    db: Session  = Depends(get_db),
    current_user = Depends(get_current_user)
):
    resumes = db.query(Resume).filter(
        Resume.user_id == current_user.id
    ).order_by(Resume.uploaded_at.desc()).all()

    if not resumes:
        return {"message": "No resumes uploaded yet"}

    return {
        "user": current_user.name,
        "resumes": [
            {
                "resume_id"  : r.id,
                "ats_score"  : r.ats_score,
                "uploaded_at": r.uploaded_at,
                "file"       : r.file_path.split("/")[-1]
            }
            for r in resumes
        ]
    }