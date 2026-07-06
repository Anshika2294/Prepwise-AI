import sys
sys.path.insert(0, "/home/anshika22/Prepwise AI/backend")

from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_question(job_role: str, resume_text: str, previous_questions: list) -> str:
    prev_q_text = "\n".join(previous_questions) if previous_questions else "None"
    prompt = f"""
You are an expert technical interviewer.
Job Role: {job_role}
Candidate Resume Summary: {resume_text[:800]}
Previously asked questions:
{prev_q_text}
Generate ONE new technical interview question relevant to the job role.
Do NOT repeat previous questions.
Ask only the question — no explanation, no numbering.
"""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text.strip()

def generate_feedback(question: str, answer: str, scores: dict) -> str:
    prompt = f"""
You are a helpful interview coach.
Interview Question: {question}
Candidate's Answer: {answer}
NLP Scores (out of 100):
- Keyword Match  : {scores['keyword_score']}
- Grammar        : {scores['grammar_score']}
- Semantic Match : {scores['semantic_score']}
- Overall        : {scores['relevance_score']}
Give constructive feedback in 3-4 sentences:
1. What was good
2. What was missing
3. A tip for better answers
Keep it encouraging and specific.
"""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text.strip()