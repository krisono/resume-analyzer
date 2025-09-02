"""
Comprehensive Resume Analysis Routes
- Enhanced analysis with semantic similarity
- User authentication and history storage
- Advanced ATS compatibility checks
"""

from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Any, Optional
import logging

# Import services
from ..models.schemas import AnalyzeRequest
from ..services.parser_service import parse_file_to_text
from ..services.nlp_service import extract_keywords_for_jd, extract_sections, extract_named_entities, calculate_semantic_similarity, analyze_section_alignment
from ..services.scoring_service import keyword_coverage
from ..services.ats_checks import ats_heuristics, analyze_ats_compatibility
from ..services.openai_service import OpenAISuggester
from ..services.semantic_service import section_semantic_alignment
from ..services.auth_service import auth_service
from ..models.database import Analysis, AnalysisHistory, db
from ..utils.text_utils import normalize_ws
from datetime import datetime

logger = logging.getLogger(__name__)

analyze_bp = Blueprint("analyze", __name__)

def get_user_from_token() -> Optional[Dict[str, Any]]:
    """Extract user information from authorization token"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None
        
        token = auth_service.extract_token_from_header(auth_header)
        if not token:
            return None
        
        payload = auth_service.verify_token(token)
        return payload
    except Exception as e:
        logger.warning(f"Token extraction failed: {e}")
        return None

@analyze_bp.post("/analyze")
def analyze():
    """Comprehensive resume analysis with all features"""
    try:
        # Get user from token (optional for anonymous analysis)
        user_payload = get_user_from_token()
        user_id = user_payload.get("user_id") if user_payload else None
        
        resume_text = None
        jd_text = None
        file_format = "pdf"  # Default format

        # Handle different input formats
        if request.content_type and "application/json" in request.content_type:
            data = request.get_json(silent=True) or {}
            req = AnalyzeRequest(**data)
            resume_text = normalize_ws(req.resume_text or "")
            jd_text = normalize_ws(req.job_description_text or "")
            file_format = data.get("file_format", "pdf").lower()
        else:
            # Handle file uploads
            if "resume" in request.files:
                resume_text, file_format = parse_file_to_text(request.files["resume"])
                resume_text = normalize_ws(resume_text or "")
            if "job_description" in request.files:
                jd_text, _ = parse_file_to_text(request.files["job_description"])
                jd_text = normalize_ws(jd_text or "")

        if not resume_text or not jd_text:
            return jsonify({
                "error": "Both resume text and job description text are required",
                "details": "Provide resume_text and job_description_text in JSON, or upload files 'resume' and 'job_description'"
            }), 400

        # Core Analysis (Original functionality)
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

        # Enhanced Analysis Features
        enhanced_features = {}
        
        try:
            # Named entity extraction
            entities = extract_named_entities(resume_text)
            enhanced_features['entities'] = entities
            
            # Semantic similarity analysis
            semantic_similarity = calculate_semantic_similarity(resume_text, jd_text)
            enhanced_features['semantic_similarity'] = semantic_similarity
            
            # Enhanced section alignment
            if resume_sections:
                enhanced_section_alignment = analyze_section_alignment(resume_sections, jd_text)
                enhanced_features['section_alignment'] = enhanced_section_alignment
            
            # Enhanced ATS analysis
            ats_analysis = analyze_ats_compatibility(resume_text, file_format)
            enhanced_features['ats_analysis'] = ats_analysis
            
            # Content quality analysis
            content_quality = _analyze_content_quality(resume_text, jd_text)
            enhanced_features['content_quality'] = content_quality
            
        except Exception as e:
            logger.warning(f"Enhanced analysis failed: {e}")
            enhanced_features['error'] = str(e)

        # Prepare response
        response_data = {
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
            "enhanced_features": enhanced_features,
            "analysis_metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "file_format": file_format,
                "authenticated": user_id is not None
            }
        }

        # Save to database if user is authenticated
        if user_id:
            try:
                _save_analysis_to_db(user_id, response_data)
                response_data["analysis_metadata"]["saved_to_history"] = True
            except Exception as e:
                logger.error(f"Failed to save analysis: {e}")
                response_data["analysis_metadata"]["saved_to_history"] = False

        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({"error": "Analysis failed", "details": str(e)}), 500

def _analyze_content_quality(resume_text: str, jd_text: str) -> Dict[str, Any]:
    """Analyze overall content quality and completeness"""
    analysis = {
        'word_count': len(resume_text.split()),
        'character_count': len(resume_text),
        'sentence_count': len([s for s in resume_text.split('.') if s.strip()]),
        'readability': {},
        'completeness': {},
        'recommendations': []
    }
    
    # Basic readability metrics
    avg_words_per_sentence = analysis['word_count'] / max(analysis['sentence_count'], 1)
    analysis['readability'] = {
        'avg_words_per_sentence': round(avg_words_per_sentence, 1),
        'complexity_level': 'Simple' if avg_words_per_sentence < 15 else 'Complex'
    }
    
    # Content completeness check
    essential_sections = ['experience', 'education', 'skills']
    resume_lower = resume_text.lower()
    
    completeness = {}
    for section in essential_sections:
        completeness[section] = section in resume_lower
    
    missing_sections = [s for s, present in completeness.items() if not present]
    
    analysis['completeness'] = {
        'essential_sections_present': completeness,
        'missing_sections': missing_sections,
        'completeness_score': int((len(essential_sections) - len(missing_sections)) / len(essential_sections) * 100)
    }
    
    # Generate recommendations
    if analysis['word_count'] < 200:
        analysis['recommendations'].append('Resume appears too short - consider adding more detail')
    elif analysis['word_count'] > 800:
        analysis['recommendations'].append('Resume might be too long - consider condensing')
    
    if missing_sections:
        analysis['recommendations'].append(f'Consider adding missing sections: {", ".join(missing_sections)}')
    
    if avg_words_per_sentence > 20:
        analysis['recommendations'].append('Consider using shorter sentences for better readability')
    
    return analysis

def _save_analysis_to_db(user_id: int, analysis_data: Dict[str, Any]) -> Optional[int]:
    """Save analysis results to database"""
    try:
        # Create analysis record
        analysis = Analysis(
            user_id=user_id,
            overall_score=analysis_data.get('scores', {}).get('overall_score', 0),
            created_at=datetime.utcnow()
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        # Create history record
        history = AnalysisHistory(
            user_id=user_id,
            analysis_id=analysis.id,
            action='analysis_completed',
            timestamp=datetime.utcnow()
        )
        
        db.session.add(history)
        db.session.commit()
        
        logger.info(f"Saved analysis {analysis.id} for user {user_id}")
        return analysis.id
        
    except Exception as e:
        logger.error(f"Failed to save analysis to database: {e}")
        db.session.rollback()
        return None

@analyze_bp.route("/analyze-history", methods=["GET"])
def get_analysis_history():
    """Get user's analysis history"""
    try:
        # Require authentication
        user_payload = get_user_from_token()
        if not user_payload:
            return jsonify({"error": "Authentication required"}), 401
        
        user_id = user_payload["user_id"]
        limit = int(request.args.get("limit", 10))
        
        # Get analysis history
        analyses = Analysis.query.filter_by(user_id=user_id)\
                                .order_by(Analysis.created_at.desc())\
                                .limit(limit)\
                                .all()
        
        history = []
        for analysis in analyses:
            history.append({
                'id': analysis.id,
                'overall_score': analysis.overall_score,
                'created_at': analysis.created_at.isoformat()
            })
        
        return jsonify({
            "history": history,
            "total_count": len(history),
            "user_id": user_id
        }), 200
        
    except ValueError:
        return jsonify({"error": "Invalid limit parameter"}), 400
    except Exception as e:
        logger.error(f"History fetch error: {e}")
        return jsonify({"error": "Failed to fetch analysis history"}), 500
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