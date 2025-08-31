from __future__ import annotations
from typing import Dict, List
from flask import current_app
from .embeddings_service import Embeddings
from ..models.schemas import SectionScore

def section_semantic_alignment(resume_sections: Dict[str, str], jd_text: str) -> List[SectionScore]:
    settings = current_app.config.get("SETTINGS")
    emb = Embeddings(getattr(settings, "OPENAI_API_KEY", None))
    out: List[SectionScore] = []
    for name, content in resume_sections.items():
        sim = emb.similarity(content, jd_text)
        missing_terms: List[str] = []
        for kw in set((jd_text or "").lower().split()):
            if len(kw) > 3 and kw not in (content or "").lower():
                missing_terms.append(kw)
        out.append(SectionScore(section=name, similarity=sim, missing_terms=missing_terms[:8]))
    out.sort(key=lambda s: s.similarity, reverse=True)
    return out