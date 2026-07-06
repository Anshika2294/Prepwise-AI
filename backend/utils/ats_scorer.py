import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.resume_parser import extract_skills, extract_experience_years
from .resume_parser import extract_skills, extract_experience_years

# Job role ke liye expected keywords
JOB_ROLE_KEYWORDS = {
    "python developer": [
        "python", "fastapi", "django", "flask", "rest api", "sql",
        "git", "docker", "postgresql", "pandas", "numpy"
    ],
    "data scientist": [
        "python", "machine learning", "deep learning", "pandas", "numpy",
        "scikit-learn", "tensorflow", "pytorch", "sql", "data analysis",
        "nlp", "statistics", "matplotlib"
    ],
    "frontend developer": [
        "javascript", "react", "html", "css", "typescript", "git",
        "rest api", "redux", "node.js", "responsive design"
    ],
    "backend developer": [
        "python", "java", "node.js", "sql", "mysql", "postgresql",
        "rest api", "docker", "git", "mongodb", "redis"
    ],
    "fullstack developer": [
        "javascript", "react", "node.js", "python", "sql", "rest api",
        "git", "docker", "html", "css", "mongodb"
    ],
    "ml engineer": [
        "python", "machine learning", "deep learning", "tensorflow",
        "pytorch", "mlops", "docker", "kubernetes", "sql", "scikit-learn"
    ],
}

def calculate_ats_score(resume_text: str, job_role: str) -> dict:
    job_role = job_role.lower().strip()

    # Job role ke liye keywords lo (ya generic use karo)
    expected_keywords = JOB_ROLE_KEYWORDS.get(
        job_role,
        ["python", "sql", "git", "communication", "problem solving"]
    )

    # Resume mein jo skills mili hain
    resume_skills = extract_skills(resume_text)
    experience    = extract_experience_years(resume_text)

    # Skill match score (0-60 points)
    matched = [s for s in expected_keywords if s in resume_skills]
    skill_score = round((len(matched) / len(expected_keywords)) * 60, 2)

    # TF-IDF cosine similarity score (0-30 points)
    job_description = " ".join(expected_keywords)
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([resume_text.lower(), job_description])
        similarity   = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        tfidf_score  = round(similarity * 30, 2)
    except Exception:
        tfidf_score = 0.0

    # Experience bonus (0-10 points)
    exp_score = min(experience * 2, 10)

    total_score = round(skill_score + tfidf_score + exp_score, 2)
    total_score = min(total_score, 100.0)  # cap at 100

    return {
        "total_score"       : total_score,
        "skill_score"       : skill_score,
        "tfidf_score"       : tfidf_score,
        "experience_score"  : exp_score,
        "matched_skills"    : matched,
        "missing_skills"    : [s for s in expected_keywords if s not in resume_skills],
        "experience_years"  : experience,
    }