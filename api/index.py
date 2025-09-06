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
                
                # Simple mock analysis with proper structure
                overall_score = random.randint(70, 95)
                ats_score = random.randint(80, 95)
                keyword_score = random.randint(60, 90)
                
                mock_response = {
                    "scores": {
                        "overall_score": overall_score,
                        "ats_score": ats_score,
                        "keyword_score": keyword_score,
                        "checks": {
                            "has_contact_info": True,
                            "proper_formatting": True,
                            "keyword_density": True
                        }
                    },
                    "summary": f"Your resume scored {overall_score}% overall. Strong ATS compatibility at {ats_score}% with {keyword_score}% keyword matching.",
                    "keywords": [
                        {"keyword": "Python", "in_resume": True, "context": "Programming"},
                        {"keyword": "React", "in_resume": True, "context": "Frontend"},
                        {"keyword": "Machine Learning", "in_resume": False, "context": "Skills"},
                        {"keyword": "AWS", "in_resume": True, "context": "Cloud"},
                        {"keyword": "Docker", "in_resume": False, "context": "DevOps"}
                    ],
                    "missing_keywords": ["Machine Learning", "Docker", "Kubernetes"],
                    "coverage": {
                        "total_keywords": 15,
                        "matched_keywords": 10,
                        "percentage": 67
                    },
                    "suggestions": [
                        "Add more specific technical skills mentioned in the job description",
                        "Include quantifiable achievements with numbers and percentages", 
                        "Optimize formatting for better ATS scanning",
                        "Add missing keywords: Machine Learning, Docker"
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
                error_response = {"error": f"Analysis failed: {str(e)}"}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        elif self.path == '/api/report/pdf':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                # Generate a basic valid PDF
                pdf_content = self.create_basic_pdf()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/pdf')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Disposition', 'attachment; filename="resume-analysis-report.pdf"')
                self.send_header('Content-Length', str(len(pdf_content)))
                self.end_headers()
                self.wfile.write(pdf_content)
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                error_response = {"error": f"PDF generation failed: {str(e)}"}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        else:
            self.send_error(404)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def create_basic_pdf(self):
        # Create a minimal valid PDF structure
        overall_score = random.randint(70, 95)
        ats_score = random.randint(80, 95) 
        keyword_score = random.randint(60, 90)
        
        pdf_content = f"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Resources <<
/Font <<
/F1 4 0 R
>>
>>
/Contents 5 0 R
>>
endobj

4 0 obj
<<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
endobj

5 0 obj
<<
/Length 400
>>
stream
BT
/F1 24 Tf
50 700 Td
(Resume Analysis Report) Tj
0 -50 Td
/F1 14 Tf
(Generated on: September 5, 2025) Tj
0 -30 Td
(Overall Score: {overall_score}%) Tj
0 -25 Td
(ATS Compatibility: {ats_score}%) Tj
0 -25 Td
(Keyword Match: {keyword_score}%) Tj
0 -40 Td
(Suggestions:) Tj
0 -20 Td
(- Add more specific technical skills) Tj
0 -15 Td
(- Include quantifiable achievements) Tj
0 -15 Td
(- Optimize for ATS scanning) Tj
ET
endstream
endobj

xref
0 6
0000000000 65535 f 
0000000010 00000 n 
0000000053 00000 n 
0000000110 00000 n 
0000000251 00000 n 
0000000318 00000 n 
trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
770
%%EOF"""
        return pdf_content.encode('utf-8')
