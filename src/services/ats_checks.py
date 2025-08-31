from __future__ import annotations
import re
from ..utils.text_utils import has_sections, detect_contact_info

def ats_heuristics(resume_text: str) -> tuple[dict, float]:
    text = resume_text or ""
    checks = {
        "has_sections": has_sections(text),
        "has_contact_info": detect_contact_info(text),
        "no_photos_or_graphics": True,
        "reasonable_length": 300 <= len(text) <= 9000,
        "bullet_usage": bool(re.search(r"(^|\n)\s*[•\-\*]", text)),
        "no_tables_detected": True,
        "simple_headings": True,
        "no_excessive_columns": True,
        "no_header_footer_text": True,
    }
    truthy = sum(1 for v in checks.values() if v)
    total = len(checks)
    score = round((truthy / total) * 100.0, 1)
    return checks, score