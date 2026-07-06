import sys; sys.path.insert(0, r"/home/anshika22/Prepwise AI/backend")
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import os, shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from database import get_db
from models import Resume, User
from schemas import ResumeOut
from utils.resume_parser import extract_text
from utils.ats_scorer import calculate_ats_score
from utils.jwt_handler import verify_token

router = APIRouter(prefix="/resume", tags=["Resume"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

UPLOAD_DIR = "uploads/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/upload", response_model=ResumeOut)
async def upload_resume(
    file: UploadFile = File(...),
    job_role: str    = Form(...),
    db: Session      = Depends(get_db),
    current_user     = Depends(get_current_user)
):
    # File type check
    allowed = ["application/pdf",
               "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files allowed")

    # Save file
    file_path = os.path.join(UPLOAD_DIR, f"{current_user.id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Text extract karo
    try:
        resume_text = extract_text(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")

    # ATS Score calculate karo
    ats_result = calculate_ats_score(resume_text, job_role)

    # DB mein save karo
    resume = Resume(
        user_id     = current_user.id,
        file_path   = file_path,
        ats_score   = ats_result["total_score"],
        parsed_text = resume_text
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return resume


@router.get("/ats-result/{resume_id}")
def get_ats_result(
    resume_id: int,
    job_role: str,
    db: Session  = Depends(get_db),
    current_user = Depends(get_current_user)
):
    resume = db.query(Resume).filter(
        Resume.id      == resume_id,
        Resume.user_id == current_user.id
    ).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    ats_result = calculate_ats_score(resume.parsed_text, job_role)
    return {
        "resume_id"        : resume_id,
        "job_role"         : job_role,
        "ats_score"        : ats_result["total_score"],
        "skill_score"      : ats_result["skill_score"],
        "tfidf_score"      : ats_result["tfidf_score"],
        "experience_score" : ats_result["experience_score"],
        "matched_skills"   : ats_result["matched_skills"],
        "missing_skills"   : ats_result["missing_skills"],
        "experience_years" : ats_result["experience_years"],
    }


@router.get("/my-resumes")
def get_my_resumes(
    db: Session  = Depends(get_db),
    current_user = Depends(get_current_user)
):
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    return resumes