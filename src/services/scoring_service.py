from __future__ import annotations
from typing import List, Tuple
from rapidfuzz import fuzz
from ..utils.text_utils import find_snippets

def keyword_coverage(resume_text: str, jd_keywords: List[str]) -> Tuple[List[dict], List[str], float]:
    coverage, missing = [], []
    resume_lower = (resume_text or "").lower()
    hits = 0
    for kw in jd_keywords:
        kw_low = kw.lower()
        in_resume = False
        count = 0
        if kw_low in resume_lower:
            in_resume = True
            count = resume_lower.count(kw_low)
        else:
            if fuzz.partial_ratio(kw_low, resume_lower) >= 90:
                in_resume = True
                count = 1
        if in_resume:
            hits += 1
            snippets = find_snippets(resume_text, kw, window=80)
            coverage.append({"keyword": kw, "in_resume": True, "frequency": count, "context_snippets": snippets})
        else:
            missing.append(kw)
            coverage.append({"keyword": kw, "in_resume": False, "frequency": 0, "context_snippets": []})
    keyword_score = (hits / max(1, len(jd_keywords))) * 100.0
    return coverage, missing, round(keyword_score, 1)