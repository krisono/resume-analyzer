import re
from typing import List

def normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()

def split_sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text or "") if s.strip()]

def find_snippets(text: str, keyword: str, window: int = 80) -> List[str]:
    out = []
    for m in re.finditer(re.escape(keyword), text, flags=re.I):
        start = max(0, m.start() - window)
        end = min(len(text), m.end() + window)
        out.append(text[start:end].strip())
    return out[:5]

SECTION_MARKERS = [
    r"summary|profile|objective",
    r"experience|employment|work history",
    r"education",
    r"skills|technologies|tooling",
    r"projects",
    r"certifications|licenses",
]

def has_sections(text: str) -> bool:
    t = text.lower()
    return sum(bool(re.search(pat, t)) for pat in SECTION_MARKERS) >= 3

def detect_contact_info(text: str) -> bool:
    has_email = bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text))
    has_phone = bool(re.search(r"\+?\d[\d\s().-]{7,}\d", text))
    return has_email and has_phone