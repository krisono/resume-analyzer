import json
import random
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/analyze':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                resume_text = data.get('resume_text', '')
                job_description_text = data.get('job_description_text', '')
                
                # Simple mock analysis
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
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                self.wfile.write(json.dumps(mock_response).encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_GET(self):
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "message": "API is running"}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
