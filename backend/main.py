from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import sys
sys.path.insert(0, "/home/anshika22/Prepwise AI/backend")

from database import engine, Base
from routers import auth, resume, interview, report

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Mock Interview API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(resume.router)
app.include_router(interview.router)
app.include_router(report.router)

@app.get("/")
def home():
    return {"message": "AI Mock Interview API is running ✅"}