# Enhanced Flask Routes for Resume Generator
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import tempfile
from io import BytesIO
import json
import logging

from src.services.resume_generator import (
    ResumeParser, JobDescriptionAnalyzer, BulletRewriter, 
    ATSValidator, ResumeGenerator, ResumeSchema
)
from src.services.file_parser import parse_pdf, parse_docx, parse_txt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize services
resume_parser = ResumeParser()
jd_analyzer = JobDescriptionAnalyzer()
bullet_rewriter = BulletRewriter()
ats_validator = ATSValidator()
resume_generator = ResumeGenerator()

@app.route('/api/analyze', methods=['POST'])
def analyze_resume():
    """Analyze resume against job description"""
    try:
        # Handle file upload or text input
        resume_text = ""
        job_description = ""
        
        if 'resume' in request.files:
            # File upload mode
            resume_file = request.files['resume']
            if resume_file and resume_file.filename:
                filename = secure_filename(resume_file.filename)
                file_ext = filename.lower().split('.')[-1]
                
                # Parse file based on extension
                if file_ext == 'pdf':
                    resume_text = parse_pdf(resume_file)
                elif file_ext in ['docx', 'doc']:
                    resume_text = parse_docx(resume_file)
                elif file_ext == 'txt':
                    resume_text = parse_txt(resume_file)
                else:
                    return jsonify({'error': 'Unsupported file format'}), 400
            
            job_description = request.form.get('job_description', '')
        else:
            # JSON mode
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            resume_text = data.get('resume_text', '')
            job_description = data.get('job_description', '')
        
        if not resume_text or not job_description:
            return jsonify({'error': 'Both resume and job description are required'}), 400
        
        # Parse resume
        parsed_resume = resume_parser.parse_text(resume_text)
        
        # Analyze job description
        options = request.get_json() or {}
        use_llm = options.get('use_llm', False)
        jd_keywords = jd_analyzer.extract_keywords(job_description, use_llm)
        
        # Calculate scores
        scores = calculate_scores(parsed_resume, jd_keywords, job_description)
        
        # Find gaps
        gaps = find_keyword_gaps(parsed_resume, jd_keywords)
        
        # ATS compliance check
        compliance_issues = ats_validator.validate(parsed_resume)
        
        # Convert ResumeSchema to dict for JSON serialization
        resume_dict = {
            'contact': parsed_resume.contact,
            'summary': parsed_resume.summary,
            'skills': parsed_resume.skills,
            'experience': parsed_resume.experience,
            'projects': parsed_resume.projects,
            'education': parsed_resume.education,
            'certifications': parsed_resume.certifications,
            'links': parsed_resume.links
        }
        
        response = {
            'parsed_resume': resume_dict,
            'scores': scores,
            'gaps': gaps,
            'compliance_issues': compliance_issues,
            'keywords_found': jd_keywords
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        return jsonify({'error': 'Analysis failed', 'details': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate_resume():
    """Generate ATS-optimized resume"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Convert dict back to ResumeSchema
        resume_data_dict = data.get('resume_data', {})
        resume_data = ResumeSchema(
            contact=resume_data_dict.get('contact', {}),
            summary=resume_data_dict.get('summary', ''),
            skills=resume_data_dict.get('skills', []),
            experience=resume_data_dict.get('experience', []),
            projects=resume_data_dict.get('projects', []),
            education=resume_data_dict.get('education', []),
            certifications=resume_data_dict.get('certifications', []),
            links=resume_data_dict.get('links', {})
        )
        
        template = data.get('template', 'plain')
        format_type = data.get('format', 'pdf')
        
        # Generate resume
        resume_bytes = resume_generator.generate(resume_data, template, format_type)
        
        # Return file
        if format_type == 'pdf':
            mimetype = 'application/pdf'
            filename = f'resume_{template}.pdf'
        elif format_type == 'docx':
            mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            filename = f'resume_{template}.docx'
        else:  # html
            mimetype = 'text/html'
            filename = f'resume_{template}.html'
        
        return send_file(
            BytesIO(resume_bytes),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Generation failed: {str(e)}")
        return jsonify({'error': 'Generation failed', 'details': str(e)}), 500

@app.route('/api/rewrite-bullets', methods=['POST'])
def rewrite_bullets():
    """Rewrite bullet points for impact"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        bullets = data.get('bullets', [])
        job_description = data.get('job_description', '')
        tone = data.get('tone', 'professional')
        
        if not bullets:
            return jsonify({'error': 'No bullets provided'}), 400
        
        # Rewrite bullets
        rewrites = bullet_rewriter.rewrite_bullets(bullets, job_description, tone)
        
        return jsonify({'rewrites': rewrites})
        
    except Exception as e:
        logger.error(f"Bullet rewriting failed: {str(e)}")
        return jsonify({'error': 'Rewriting failed', 'details': str(e)}), 500

@app.route('/api/keywords', methods=['POST'])
def extract_keywords():
    """Extract keywords from job description"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        job_description = data.get('job_description', '')
        use_llm = data.get('use_llm', False)
        
        if not job_description:
            return jsonify({'error': 'Job description is required'}), 400
        
        # Extract keywords
        keywords = jd_analyzer.extract_keywords(job_description, use_llm)
        
        return jsonify({'keywords': keywords})
        
    except Exception as e:
        logger.error(f"Keyword extraction failed: {str(e)}")
        return jsonify({'error': 'Keyword extraction failed', 'details': str(e)}), 500

def calculate_scores(resume_data: ResumeSchema, jd_keywords: list, jd_text: str) -> dict:
    """Calculate various scores for the resume"""
    
    # Keyword coverage score
    resume_text = f"{resume_data.summary} {' '.join(resume_data.skills)}"
    for exp in resume_data.experience:
        resume_text += f" {' '.join(exp.get('bullets', []))}"
    
    resume_text_lower = resume_text.lower()
    
    keyword_matches = 0
    total_keywords = len(jd_keywords)
    
    for keyword in jd_keywords:
        if keyword['term'].lower() in resume_text_lower:
            keyword_matches += keyword.get('importance', 0.5)
    
    keyword_score = (keyword_matches / max(total_keywords, 1)) * 100 if total_keywords > 0 else 0
    
    # ATS score based on compliance
    ats_issues = ats_validator.validate(resume_data)
    critical_issues = sum(1 for issue in ats_issues if issue['severity'] == 'critical')
    high_issues = sum(1 for issue in ats_issues if issue['severity'] == 'high')
    
    ats_score = max(0, 100 - (critical_issues * 30) - (high_issues * 15))
    
    # Impact density (bullets with metrics)
    total_bullets = sum(len(exp.get('bullets', [])) for exp in resume_data.experience)
    bullets_with_metrics = 0
    
    for exp in resume_data.experience:
        for bullet in exp.get('bullets', []):
            if any(char.isdigit() for char in bullet) and '%' in bullet:
                bullets_with_metrics += 1
    
    impact_density = (bullets_with_metrics / max(total_bullets, 1)) * 100 if total_bullets > 0 else 0
    
    # Overall score
    overall_score = (keyword_score * 0.4) + (ats_score * 0.4) + (impact_density * 0.2)
    
    return {
        'overall_score': round(overall_score, 1),
        'keyword_coverage': round(keyword_score, 1),
        'ats_score': round(ats_score, 1),
        'impact_density': round(impact_density, 1),
        'total_keywords': total_keywords,
        'matched_keywords': keyword_matches
    }

def find_keyword_gaps(resume_data: ResumeSchema, jd_keywords: list) -> list:
    """Find missing keywords from job description"""
    
    resume_text = f"{resume_data.summary} {' '.join(resume_data.skills)}"
    for exp in resume_data.experience:
        resume_text += f" {' '.join(exp.get('bullets', []))}"
    
    resume_text_lower = resume_text.lower()
    
    gaps = []
    for keyword in jd_keywords:
        if keyword['term'].lower() not in resume_text_lower:
            gaps.append(keyword['term'])
    
    return gaps[:10]  # Top 10 missing keywords

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'resume-generator'})

if __name__ == '__main__':
    app.run(debug=True, port=3001)
