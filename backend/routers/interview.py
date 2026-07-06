import sys
sys.path.insert(0, "/home/anshika22/Prepwise AI/backend")

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer
from database import get_db
from models import InterviewSession, InterviewQuestion, Resume, User
from schemas import SessionCreate, SessionOut, AnswerSubmit, QuestionOut
from utils.gemini_helper import generate_question, generate_feedback
from utils.nlp_scorer import full_nlp_analysis
from utils.jwt_handler import verify_token
router       = APIRouter(prefix="/interview", tags=["Interview"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ── 1. Session start karo ──
@router.post("/start", response_model=SessionOut)
def start_session(
    payload: SessionCreate,
    db: Session  = Depends(get_db),
    current_user = Depends(get_current_user)
):
    session = InterviewSession(
        user_id  = current_user.id,
        job_role = payload.job_role
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


# ── 2. Next question lo ──
@router.get("/question/{session_id}")
def get_next_question(
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

    if session.ended_at:
        raise HTTPException(status_code=400, detail="Session already ended")

    # Max 10 questions per session
    existing_questions = db.query(InterviewQuestion).filter(
        InterviewQuestion.session_id == session_id
    ).all()

    if len(existing_questions) >= 10:
        raise HTTPException(status_code=400, detail="Max 10 questions reached. End the session.")

    # Resume text lo (latest resume)
    resume = db.query(Resume).filter(
        Resume.user_id == current_user.id
    ).order_by(Resume.uploaded_at.desc()).first()

    resume_text = resume.parsed_text if resume else ""

    # Previous questions (repeat na ho)
    prev_questions = [q.question_text for q in existing_questions]

    # Gemini se question generate karo
    question_text = generate_question(session.job_role, resume_text, prev_questions)

    # DB mein save karo
    new_q = InterviewQuestion(
        session_id    = session_id,
        question_text = question_text
    )
    db.add(new_q)
    db.commit()
    db.refresh(new_q)

    return {
        "question_id"  : new_q.id,
        "question_text": new_q.question_text,
        "question_no"  : len(existing_questions) + 1
    }


# ── 3. Answer submit karo ──
@router.post("/answer")
def submit_answer(
    payload: AnswerSubmit,
    db: Session  = Depends(get_db),
    current_user = Depends(get_current_user)
):
    question = db.query(InterviewQuestion).filter(
        InterviewQuestion.id == payload.question_id
    ).first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    if question.user_answer:
        raise HTTPException(status_code=400, detail="Answer already submitted for this question")

    # NLP Analysis
    scores = full_nlp_analysis(question.question_text, payload.user_answer)

    # AI Feedback from Gemini
    feedback = generate_feedback(question.question_text, payload.user_answer, scores)

    # DB update karo
    question.user_answer     = payload.user_answer
    question.keyword_score   = scores["keyword_score"]
    question.grammar_score   = scores["grammar_score"]
    question.relevance_score = scores["relevance_score"]
    question.ai_feedback     = feedback

    db.commit()
    db.refresh(question)

    return {
        "question_id"    : question.id,
        "question_text"  : question.question_text,
        "user_answer"    : question.user_answer,
        "keyword_score"  : question.keyword_score,
        "grammar_score"  : question.grammar_score,
        "relevance_score": question.relevance_score,
        "ai_feedback"    : question.ai_feedback,
    }


# ── 4. Session end karo ──
@router.post("/end/{session_id}")
def end_session(
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

    session.ended_at = datetime.utcnow()
    db.commit()

    # Average scores calculate karo
    questions = db.query(InterviewQuestion).filter(
        InterviewQuestion.session_id == session_id
    ).all()

    answered = [q for q in questions if q.user_answer]
    if answered:
        avg_keyword   = round(sum(q.keyword_score   for q in answered) / len(answered), 2)
        avg_grammar   = round(sum(q.grammar_score   for q in answered) / len(answered), 2)
        avg_relevance = round(sum(q.relevance_score for q in answered) / len(answered), 2)
    else:
        avg_keyword = avg_grammar = avg_relevance = 0.0

    return {
        "session_id"       : session_id,
        "job_role"         : session.job_role,
        "total_questions"  : len(questions),
        "answered"         : len(answered),
        "avg_keyword_score": avg_keyword,
        "avg_grammar_score": avg_grammar,
        "avg_relevance_score": avg_relevance,
        "status"           : "Session completed"
    }


# ── 5. Session results dekho ──
@router.get("/results/{session_id}")
def get_results(
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

    return {
        "session_id" : session_id,
        "job_role"   : session.job_role,
        "started_at" : session.started_at,
        "ended_at"   : session.ended_at,
        "questions"  : [
            {
                "q_no"          : i + 1,
                "question"      : q.question_text,
                "answer"        : q.user_answer,
                "keyword_score" : q.keyword_score,
                "grammar_score" : q.grammar_score,
                "relevance_score": q.relevance_score,
                "feedback"      : q.ai_feedback,
            }
            for i, q in enumerate(questions)
        ]
    }
