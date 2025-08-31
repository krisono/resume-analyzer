from __future__ import annotations
from flask import Blueprint, request, jsonify, current_app
from ..models.schemas import AnalyzeRequest
from ..services.parser_service import parse_file_to_text
from ..services.nlp_service import extract_keywords_for_jd, extract_sections
from ..services.scoring_service import keyword_coverage
from ..services.ats_checks import ats_heuristics
from ..services.openai_service import OpenAISuggester
from ..services.semantic_service import section_semantic_alignment
from ..utils.text_utils import normalize_ws

analyze_bp = Blueprint("analyze", __name__)

@analyze_bp.post("/analyze")
def analyze():
    resume_text = None
    jd_text = None

    if request.content_type and "application/json" in request.content_type:
        data = request.get_json(silent=True) or {}
        req = AnalyzeRequest(**data)
        resume_text = normalize_ws(req.resume_text or "")
        jd_text = normalize_ws(req.job_description_text or "")
    else:
        if "resume" in request.files:
            resume_text, _ = parse_file_to_text(request.files["resume"])  # type: ignore
        if "job_description" in request.files:
            jd_text, _ = parse_file_to_text(request.files["job_description"])  # type: ignore

    resume_text = normalize_ws(resume_text or "")
    jd_text = normalize_ws(jd_text or "")

    if not resume_text or not jd_text:
        return jsonify({"error": "Provide resume_text and job_description_text in JSON, or upload files 'resume' and 'job_description'"}), 400

    jd_keywords = extract_keywords_for_jd(jd_text, limit=50)
    coverage, missing, keyword_score = keyword_coverage(resume_text, jd_keywords)
    checks, ats_score = ats_heuristics(resume_text)

    resume_sections = extract_sections(resume_text)
    section_alignment = section_semantic_alignment(resume_sections, jd_text)
    avg_section = round(sum(s.similarity for s in section_alignment)/max(1,len(section_alignment)), 1)

    overall = round(0.5 * keyword_score + 0.3 * ats_score + 0.2 * avg_section, 1)

    settings = current_app.config.get("SETTINGS")
    suggester = OpenAISuggester(getattr(settings, "OPENAI_API_KEY", None))
    suggestions = suggester.suggest(resume_text, jd_text)[:5]

    summary = (f"Keyword coverage: {keyword_score:.1f}%. ATS checks: {ats_score:.1f}%. "
               f"Section alignment avg: {avg_section}%. Overall: {overall:.1f}%. Missing {len(missing)} key terms.")

    return jsonify({
        "summary": summary,
        "missing_keywords": missing[:25],
        "coverage": coverage[:50],
        "scores": {
            "ats_score": ats_score,
            "keyword_score": keyword_score,
            "overall_score": overall,
            "checks": checks,
            "section_alignment": [s.__dict__ for s in section_alignment],
        },
        "suggestions": suggestions,
        "ai": {"openai_enabled": bool(getattr(suggester, "enabled", False))},
    })