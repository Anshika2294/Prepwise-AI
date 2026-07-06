import sys
sys.path.insert(0, "/home/anshika22/Prepwise AI/backend")

import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nlp = spacy.load("en_core_web_sm")

def keyword_score(question: str, answer: str) -> float:
    q_doc = nlp(question.lower())
    a_doc = nlp(answer.lower())
    q_keywords = set(
        token.lemma_ for token in q_doc
        if token.pos_ in ("NOUN", "VERB", "PROPN") and not token.is_stop
    )
    if not q_keywords:
        return 50.0
    a_words = set(token.lemma_ for token in a_doc)
    matched = q_keywords & a_words
    return round((len(matched) / len(q_keywords)) * 100, 2)

def grammar_score(answer: str) -> float:
    if not answer.strip():
        return 0.0
    doc       = nlp(answer)
    sentences = list(doc.sents)
    if not sentences:
        return 0.0
    good = 0
    for sent in sentences:
        tokens   = [t for t in sent if not t.is_space]
        has_subj = any(t.dep_ in ("nsubj", "nsubjpass") for t in tokens)
        has_verb = any(t.pos_ == "VERB" for t in tokens)
        if has_subj and has_verb:
            good += 1
    return round((good / len(sentences)) * 100, 2)

def semantic_similarity_score(question: str, answer: str) -> float:
    if not answer.strip():
        return 0.0
    try:
        vectorizer   = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([question.lower(), answer.lower()])
        similarity   = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(similarity * 100, 2)
    except Exception:
        return 0.0

def relevance_score(keyword: float, grammar: float, semantic: float) -> float:
    return round((keyword * 0.4) + (grammar * 0.3) + (semantic * 0.3), 2)

def full_nlp_analysis(question: str, answer: str) -> dict:
    kw  = keyword_score(question, answer)
    gr  = grammar_score(answer)
    sem = semantic_similarity_score(question, answer)
    rel = relevance_score(kw, gr, sem)
    return {
        "keyword_score"   : kw,
        "grammar_score"   : gr,
        "semantic_score"  : sem,
        "relevance_score" : rel,
    }
