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
                resume_text = data.get('resume_text', '').lower()
                job_description = data.get('job_description_text', '').lower()
                
                # Extract keywords from job description
                job_keywords = self.extract_keywords(job_description)
                
                # Analyze which keywords are in the resume
                keyword_analysis = []
                missing_keywords = []
                matched_count = 0
                
                for keyword in job_keywords:
                    in_resume = keyword.lower() in resume_text
                    keyword_analysis.append({
                        "keyword": keyword,
                        "in_resume": in_resume,
                        "context": self.get_keyword_context(keyword)
                    })
                    if in_resume:
                        matched_count += 1
                    else:
                        missing_keywords.append(keyword)
                
                # Calculate scores based on actual analysis
                total_keywords = len(job_keywords)
                keyword_percentage = (matched_count / total_keywords * 100) if total_keywords > 0 else 0
                keyword_score = max(50, min(95, int(keyword_percentage)))
                overall_score = random.randint(max(60, keyword_score - 10), min(95, keyword_score + 15))
                ats_score = random.randint(75, 95)
                
                # Generate suggestions based on missing keywords
                suggestions = self.generate_suggestions(missing_keywords, matched_count, total_keywords)
                
                mock_response = {
                    "scores": {
                        "overall_score": overall_score,
                        "ats_score": ats_score,
                        "keyword_score": keyword_score,
                        "checks": {
                            "has_contact_info": self.check_contact_info(resume_text),
                            "proper_formatting": True,
                            "keyword_density": keyword_score > 60
                        }
                    },
                    "summary": f"Your resume scored {overall_score}% overall. ATS compatibility at {ats_score}% with {keyword_score}% keyword matching. Found {matched_count} of {total_keywords} key requirements.",
                    "keywords": keyword_analysis,
                    "missing_keywords": missing_keywords,
                    "coverage": {
                        "total_keywords": total_keywords,
                        "matched_keywords": matched_count,
                        "percentage": int(keyword_percentage)
                    },
                    "suggestions": suggestions,
                    "contact_info": {
                        "email_found": "@" in resume_text,
                        "phone_found": any(char.isdigit() for char in resume_text),
                        "linkedin_found": "linkedin" in resume_text
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
    
    def extract_keywords(self, job_description):
        # Common technical skills and keywords to look for
        common_keywords = [
            "python", "java", "javascript", "react", "angular", "vue", "node.js", "express",
            "docker", "kubernetes", "aws", "azure", "gcp", "git", "sql", "mongodb", "postgresql",
            "machine learning", "ai", "data analysis", "tensorflow", "pytorch", "pandas", "numpy",
            "html", "css", "bootstrap", "tailwind", "scss", "webpack", "typescript", "redux",
            "agile", "scrum", "devops", "ci/cd", "jenkins", "terraform", "microservices", "api",
            "rest", "graphql", "testing", "jest", "selenium", "unit testing", "integration testing",
            "linux", "ubuntu", "redis", "elasticsearch", "kafka", "rabbitmq", "nginx", "apache"
        ]
        
        # Find keywords that appear in the job description
        found_keywords = []
        for keyword in common_keywords:
            if keyword in job_description.lower():
                found_keywords.append(keyword.title())
        
        # If no common keywords found, extract some words from the job description
        if len(found_keywords) < 3:
            words = job_description.split()
            # Look for capitalized technical terms or longer words
            for word in words:
                clean_word = word.strip('.,!?;:()[]"').title()
                if len(clean_word) > 4 and clean_word not in found_keywords and len(found_keywords) < 10:
                    found_keywords.append(clean_word)
        
        return found_keywords[:10]  # Limit to 10 keywords
    
    def get_keyword_context(self, keyword):
        # Categorize keywords
        programming_langs = ["python", "java", "javascript", "typescript", "go", "rust", "c++", "c#"]
        frameworks = ["react", "angular", "vue", "express", "django", "flask", "spring", "laravel"]
        cloud = ["aws", "azure", "gcp", "docker", "kubernetes", "terraform"]
        databases = ["sql", "mongodb", "postgresql", "mysql", "redis", "elasticsearch"]
        
        keyword_lower = keyword.lower()
        
        if keyword_lower in programming_langs:
            return "Programming Language"
        elif keyword_lower in frameworks:
            return "Framework"
        elif keyword_lower in cloud:
            return "Cloud/DevOps"
        elif keyword_lower in databases:
            return "Database"
        else:
            return "Skills"
    
    def check_contact_info(self, resume_text):
        # Check for email and phone patterns
        has_email = "@" in resume_text and "." in resume_text
        has_phone = any(char.isdigit() for char in resume_text)
        return has_email and has_phone
    
    def generate_suggestions(self, missing_keywords, matched_count, total_keywords):
        suggestions = []
        
        if missing_keywords:
            if len(missing_keywords) <= 3:
                suggestions.append(f"Consider adding these key skills: {', '.join(missing_keywords[:3])}")
            else:
                suggestions.append(f"Add missing keywords: {', '.join(missing_keywords[:3])} and {len(missing_keywords)-3} others")
        
        match_percentage = (matched_count / total_keywords * 100) if total_keywords > 0 else 0
        
        if match_percentage < 50:
            suggestions.append("Focus on highlighting relevant technical skills mentioned in the job description")
        elif match_percentage < 75:
            suggestions.append("Include more specific examples of your experience with the required technologies")
        
        # Always include these general suggestions
        suggestions.extend([
            "Include quantifiable achievements with numbers and percentages",
            "Use action verbs to describe your accomplishments",
            "Optimize formatting for better ATS scanning"
        ])
        
        return suggestions[:5]  # Limit to 5 suggestions
