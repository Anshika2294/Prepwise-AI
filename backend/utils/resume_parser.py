import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import spacy
import pdfplumber
import docx
import re

nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs]).strip()

def extract_text(file_path: str) -> str:
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Only PDF and DOCX supported")

def extract_keywords(text: str) -> list[str]:
    doc = nlp(text.lower())
    # Noun chunks + named entities extract karo
    keywords = set()
    for chunk in doc.noun_chunks:
        clean = chunk.text.strip()
        if len(clean) > 2:
            keywords.add(clean)
    for ent in doc.ents:
        keywords.add(ent.text.strip().lower())
    return list(keywords)

def extract_skills(text: str) -> list[str]:
    # Common tech skills list
    skill_list = [
        "python", "java", "javascript", "react", "node.js", "fastapi",
        "django", "flask", "sql", "mysql", "postgresql", "mongodb",
        "machine learning", "deep learning", "nlp", "spacy", "tensorflow",
        "pytorch", "scikit-learn", "docker", "kubernetes", "git",
        "aws", "azure", "gcp", "html", "css", "typescript", "c++", "c#",
        "data analysis", "pandas", "numpy", "opencv", "rest api",
        "graphql", "redis", "linux", "bash", "excel", "power bi"
    ]
    text_lower = text.lower()
    found = [skill for skill in skill_list if skill in text_lower]
    return found

def extract_experience_years(text: str) -> int:
    # "3 years of experience" jaisi patterns dhundho
    patterns = [
        r'(\d+)\+?\s*years?\s*of\s*experience',
        r'experience\s*of\s*(\d+)\+?\s*years?',
        r'(\d+)\+?\s*years?\s*experience',
    ]
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return int(match.group(1))
    return 0