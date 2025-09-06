import sys
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

@app.route('/health')
def health():
    return jsonify({"status": "ok", "message": "API is running"})

@app.route('/api/health')
def api_health():
    return jsonify({"status": "ok", "message": "API is running"})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        resume_text = data.get('resume_text', '')
        job_description_text = data.get('job_description_text', '')
        
        # Simple mock analysis for now
        mock_response = {
            "overall_score": random.randint(70, 95),
            "keyword_coverage": random.randint(60, 90),
            "ats_compatibility": random.randint(80, 95),
            "semantic_similarity": random.randint(65, 85),
            "keywords": [
                {"keyword": "Python", "in_resume": True, "context": "Programming"},
                {"keyword": "React", "in_resume": True, "context": "Frontend"},
                {"keyword": "Machine Learning", "in_resume": False, "context": "Skills"},
                {"keyword": "AWS", "in_resume": True, "context": "Cloud"},
                {"keyword": "Docker", "in_resume": False, "context": "DevOps"}
            ],
            "suggestions": [
                "Add more specific technical skills",
                "Include quantifiable achievements",
                "Optimize for ATS scanning"
            ],
            "contact_info": {
                "email_found": True,
                "phone_found": True,
                "linkedin_found": False
            },
            "analysis_timestamp": "2025-09-05T00:00:00Z"
        }
        
        return jsonify(mock_response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel handler
if __name__ == "__main__":
    app.run(debug=True)
