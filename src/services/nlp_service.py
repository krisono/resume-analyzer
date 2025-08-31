import re
from typing import List, Dict
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer

_nlp = spacy.load("en_core_web_sm")

SECTION_TITLES = [
    ("summary", r"summary|profile|objective"),
    ("experience", r"experience|employment|work history"),
    ("education", r"education"),
    ("skills", r"skills|technologies|tooling"),
    ("projects", r"projects"),
    ("certifications", r"certifications|licenses"),
]

def extract_sections(text: str) -> Dict[str, str]:
    t = text or ""
    lines = t.splitlines()
    current = "other"
    buckets: Dict[str, List[str]] = {k: [] for k, _ in SECTION_TITLES}
    buckets.setdefault("other", [])
    for line in lines:
        l = line.strip()
        low = l.lower()
        switched = False
        for name, pat in SECTION_TITLES:
            if re.fullmatch(fr"\s*(?:{pat})\s*:?\s*", low):
                current = name
                switched = True
                break
        if not switched:
            buckets.setdefault(current, []).append(l)
    return {k: "\n".join(v).strip() for k, v in buckets.items() if "".join(v).strip()}

def extract_noun_phrases(text: str) -> List[str]:
    if not text:
        return []
    doc = _nlp(text)
    phrases = [chunk.text.lower() for chunk in doc.noun_chunks if 2 <= len(chunk.text) <= 60]
    uniq, seen = [], set()
    for p in phrases:
        p = re.sub(r"[^a-z0-9 +#/.-]", "", p)
        p = re.sub(r"\s+", " ", p).strip()
        if p and p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq

def tfidf_top_terms(text: str, k: int = 30) -> List[str]:
    if not text:
        return []
    vec = TfidfVectorizer(max_features=1000, ngram_range=(1, 2), stop_words="english")
    _ = vec.fit_transform([text])
    feats = vec.get_feature_names_out()
    return list(feats)[:k]

def extract_keywords_for_jd(jd_text: str, limit: int = 50) -> List[str]:
    nouns = extract_noun_phrases(jd_text)
    tfidf = tfidf_top_terms(jd_text, k=limit)
    merged, seen = [], set()
    for term in nouns + tfidf:
        t = term.lower().strip()
        if t and t not in seen:
            seen.add(t)
            merged.append(t)
    return merged[:limit]