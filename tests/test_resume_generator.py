# Comprehensive Test Suite for Resume Generator
import pytest
import json
import tempfile
import os
from io import BytesIO
from unittest.mock import patch, MagicMock

from src.services.resume_generator import (
    ResumeParser, JobDescriptionAnalyzer, BulletRewriter,
    ATSValidator, ResumeGenerator, ResumeSchema
)
from src.services.file_parser import parse_pdf, parse_docx, parse_txt, clean_extracted_text

# Test data
SAMPLE_RESUME_TEXT = """
John Smith
john.smith@email.com
(555) 123-4567
San Francisco, CA

SUMMARY
Software Engineer with 5 years of experience in Python and React development.

TECHNICAL SKILLS
Python, React, JavaScript, PostgreSQL, AWS, Docker, Git

EXPERIENCE

Senior Software Engineer
TechCorp Inc | January 2022 - Present
• Built microservices architecture serving 1M+ users using Python/Django
• Led team of 3 developers delivering features 25% faster
• Optimized database queries reducing response time by 40%

Software Developer  
StartupXYZ | June 2019 - December 2021
• Developed React frontend applications for 50K+ users
• Implemented REST APIs using Flask and PostgreSQL
• Reduced page load time from 3s to 800ms through optimization

EDUCATION
Stanford University | BS Computer Science | 2019

CERTIFICATIONS
AWS Solutions Architect, Docker Certified Associate
"""

SAMPLE_JOB_DESCRIPTION = """
Senior Full Stack Engineer

We're seeking a Senior Full Stack Engineer with expertise in Python, React, and cloud technologies.

Required Skills:
- Python (Django/Flask) - 3+ years
- React.js - 2+ years  
- PostgreSQL or MySQL
- AWS (EC2, S3, Lambda)
- Docker containerization
- REST API development
- Git version control

Preferred:
- Kubernetes
- GraphQL
- Redis caching
- CI/CD pipelines
- Team leadership experience

The ideal candidate will have experience building scalable applications serving thousands of users and leading small development teams.
"""

class TestResumeParser:
    """Test resume parsing functionality"""
    
    def test_parse_basic_resume(self):
        parser = ResumeParser()
        result = parser.parse_text(SAMPLE_RESUME_TEXT)
        
        # Check contact information
        assert result.contact['name'] == 'John Smith'
        assert result.contact['email'] == 'john.smith@email.com'
        assert result.contact['phone'] == '(555) 123-4567'
        
        # Check skills extraction
        assert 'Python' in result.skills
        assert 'React' in result.skills
        assert 'PostgreSQL' in result.skills
        
        # Check experience extraction
        assert len(result.experience) >= 2
        assert any('TechCorp' in exp.get('company', '') for exp in result.experience)
        
        # Check summary
        assert 'Software Engineer' in result.summary
        assert '5 years' in result.summary

    def test_section_detection(self):
        parser = ResumeParser()
        sections = parser._detect_sections(SAMPLE_RESUME_TEXT)
        
        assert 'experience' in sections
        assert 'skills' in sections
        assert 'education' in sections
        assert 'certifications' in sections

    def test_contact_extraction(self):
        parser = ResumeParser()
        contact = parser._extract_contact(SAMPLE_RESUME_TEXT)
        
        assert contact['email'] == 'john.smith@email.com'
        assert contact['phone'] == '(555) 123-4567'
        assert 'John Smith' in contact['name']

    def test_skills_extraction(self):
        parser = ResumeParser()
        skills = parser._extract_skills("Python, React, JavaScript, PostgreSQL, AWS, Docker")
        
        assert 'Python' in skills
        assert 'React' in skills
        assert 'PostgreSQL' in skills
        assert len(skills) > 0

class TestJobDescriptionAnalyzer:
    """Test job description analysis"""
    
    def test_keyword_extraction_heuristic(self):
        analyzer = JobDescriptionAnalyzer()
        keywords = analyzer._extract_keywords_heuristic(SAMPLE_JOB_DESCRIPTION)
        
        # Check for important keywords
        keyword_terms = [kw['term'] for kw in keywords]
        assert 'Python' in keyword_terms
        assert 'React' in keyword_terms
        assert 'PostgreSQL' in keyword_terms
        assert 'AWS' in keyword_terms
        
        # Check categories are assigned
        for kw in keywords:
            assert 'category' in kw
            assert 'importance' in kw
            assert isinstance(kw['importance'], (int, float))

    def test_importance_calculation(self):
        analyzer = JobDescriptionAnalyzer()
        
        # Test high importance for frequently mentioned terms
        high_importance = analyzer._calculate_importance('Python', 'Python Python Python Django Flask')
        low_importance = analyzer._calculate_importance('Python', 'Java JavaScript')
        
        assert high_importance > low_importance

    @patch('openai.ChatCompletion.create')
    def test_llm_keyword_extraction(self, mock_openai):
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps([
            {"term": "Python", "category": "language", "importance": 1.0},
            {"term": "React", "category": "framework", "importance": 0.9}
        ])
        mock_openai.return_value = mock_response
        
        analyzer = JobDescriptionAnalyzer()
        keywords = analyzer._extract_keywords_llm(SAMPLE_JOB_DESCRIPTION)
        
        assert len(keywords) == 2
        assert keywords[0]['term'] == 'Python'
        assert keywords[1]['term'] == 'React'

class TestBulletRewriter:
    """Test bullet point rewriting"""
    
    def test_bullet_rewriting(self):
        rewriter = BulletRewriter()
        bullets = [
            "I worked on the backend API",
            "Helped improve performance",
            "Was responsible for database optimization"
        ]
        
        results = rewriter.rewrite_bullets(bullets, SAMPLE_JOB_DESCRIPTION)
        
        assert len(results) == 3
        
        for result in results:
            assert 'original' in result
            assert 'rewritten' in result
            assert 'improvements' in result
            
            # Check that first-person pronouns are removed
            assert 'I ' not in result['rewritten']
            assert not result['rewritten'].startswith('I ')

    def test_action_verb_addition(self):
        rewriter = BulletRewriter()
        
        # Test bullet without action verb
        weak_bullet = "responsible for database management"
        rewritten = rewriter._rewrite_single_bullet(weak_bullet, "", "professional")
        
        # Should start with an action verb
        first_word = rewritten.split()[0]
        assert first_word in rewriter.action_verbs or first_word.startswith(tuple(rewriter.action_verbs))

    def test_improvement_identification(self):
        rewriter = BulletRewriter()
        
        original = "I was responsible for working on backend systems"
        rewritten = "Developed backend systems"
        
        improvements = rewriter._identify_improvements(original, rewritten)
        
        assert "Removed first-person pronouns" in improvements
        assert "Made more concise" in improvements

class TestATSValidator:
    """Test ATS compliance validation"""
    
    def test_basic_validation(self):
        validator = ATSValidator()
        
        # Create test resume data
        resume_data = ResumeSchema(
            contact={'name': 'John Smith', 'email': 'john@email.com', 'phone': '555-123-4567'},
            summary='Software Engineer with 5 years experience',
            skills=['Python', 'React', 'PostgreSQL'],
            experience=[{
                'company': 'TechCorp',
                'role': 'Engineer',
                'bullets': ['Built applications', 'Led team']
            }],
            projects=[],
            education=[{'school': 'Stanford', 'degree': 'BS CS', 'grad': '2019'}],
            certifications=['AWS'],
            links={'github': 'github.com/john'}
        )
        
        issues = validator.validate(resume_data)
        
        # Should have minimal issues for well-structured resume
        critical_issues = [issue for issue in issues if issue['severity'] == 'critical']
        assert len(critical_issues) == 0

    def test_missing_contact_validation(self):
        validator = ATSValidator()
        
        # Create resume with missing contact info
        resume_data = ResumeSchema(
            contact={'name': 'John Smith', 'email': '', 'phone': ''},
            summary='Engineer',
            skills=[],
            experience=[],
            projects=[],
            education=[],
            certifications=[],
            links={}
        )
        
        issues = validator.validate(resume_data)
        
        # Should flag missing email and phone
        issue_messages = [issue['issue'] for issue in issues]
        assert any('email' in msg.lower() for msg in issue_messages)
        assert any('phone' in msg.lower() for msg in issue_messages)

class TestResumeGenerator:
    """Test resume generation in different formats"""
    
    def test_plain_template_generation(self):
        generator = ResumeGenerator()
        
        # Create test data
        resume_data = ResumeSchema(
            contact={'name': 'John Smith', 'email': 'john@email.com', 'phone': '555-123-4567'},
            summary='Software Engineer',
            skills=['Python', 'React'],
            experience=[{
                'company': 'TechCorp',
                'role': 'Engineer',
                'start': '2022-01',
                'end': 'Present',
                'bullets': ['Built applications']
            }],
            projects=[],
            education=[],
            certifications=[],
            links={}
        )
        
        html_output = generator._generate_plain_template(resume_data)
        
        assert 'John Smith' in html_output
        assert 'john@email.com' in html_output
        assert 'TechCorp' in html_output
        assert 'Built applications' in html_output

    def test_html_generation(self):
        generator = ResumeGenerator()
        
        resume_data = ResumeSchema(
            contact={'name': 'Test User', 'email': 'test@email.com'},
            summary='Test summary',
            skills=['Python'],
            experience=[],
            projects=[],
            education=[],
            certifications=[],
            links={}
        )
        
        html_bytes = generator.generate(resume_data, 'plain', 'html')
        html_content = html_bytes.decode('utf-8')
        
        assert '<!DOCTYPE html>' in html_content
        assert 'Test User' in html_content

    def test_template_selection(self):
        generator = ResumeGenerator()
        
        # Test all templates exist
        assert 'plain' in generator.templates
        assert 'compact' in generator.templates
        assert 'engineer' in generator.templates
        
        # Test invalid template raises error
        with pytest.raises(ValueError):
            generator.generate(None, 'invalid_template', 'html')

class TestFileParser:
    """Test file parsing utilities"""
    
    def test_text_cleaning(self):
        dirty_text = "This   has    excessive   whitespace\n\n\n\nAnd too many line breaks"
        cleaned = clean_extracted_text(dirty_text)
        
        assert '   ' not in cleaned
        assert '\n\n\n' not in cleaned
        assert len(cleaned) > 0

    def test_txt_parsing(self):
        # Create temporary text file
        test_content = "John Smith\njohn@email.com\nSoftware Engineer"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            f.flush()
            
            with open(f.name, 'rb') as file_obj:
                result = parse_txt(file_obj)
                
                assert 'John Smith' in result
                assert 'john@email.com' in result
                assert 'Software Engineer' in result
        
        # Clean up
        os.unlink(f.name)

class TestIntegration:
    """Integration tests for full workflow"""
    
    def test_full_analysis_workflow(self):
        """Test complete resume analysis workflow"""
        
        # Parse resume
        parser = ResumeParser()
        resume_data = parser.parse_text(SAMPLE_RESUME_TEXT)
        
        # Analyze job description
        jd_analyzer = JobDescriptionAnalyzer()
        keywords = jd_analyzer.extract_keywords(SAMPLE_JOB_DESCRIPTION, use_llm=False)
        
        # Validate ATS compliance
        validator = ATSValidator()
        issues = validator.validate(resume_data)
        
        # Generate optimized resume
        generator = ResumeGenerator()
        html_output = generator.generate(resume_data, 'plain', 'html')
        
        # Verify results
        assert resume_data.contact['name'] == 'John Smith'
        assert len(keywords) > 0
        assert isinstance(issues, list)
        assert len(html_output) > 0

    def test_bullet_rewriting_integration(self):
        """Test bullet point rewriting with job context"""
        
        rewriter = BulletRewriter()
        parser = ResumeParser()
        
        # Parse resume to get existing bullets
        resume_data = parser.parse_text(SAMPLE_RESUME_TEXT)
        
        # Extract bullets from first experience
        if resume_data.experience:
            bullets = resume_data.experience[0].get('bullets', [])
            
            # Rewrite bullets with job context
            results = rewriter.rewrite_bullets(bullets, SAMPLE_JOB_DESCRIPTION)
            
            assert len(results) > 0
            
            for result in results:
                # Check improvements
                assert len(result['improvements']) >= 0
                
                # Check no first-person pronouns
                assert 'I ' not in result['rewritten']

    def test_scoring_calculation(self):
        """Test scoring algorithm"""
        from src.routes.resume_routes import calculate_scores
        
        parser = ResumeParser()
        jd_analyzer = JobDescriptionAnalyzer()
        
        resume_data = parser.parse_text(SAMPLE_RESUME_TEXT)
        keywords = jd_analyzer.extract_keywords(SAMPLE_JOB_DESCRIPTION, use_llm=False)
        
        scores = calculate_scores(resume_data, keywords, SAMPLE_JOB_DESCRIPTION)
        
        assert 'overall_score' in scores
        assert 'keyword_coverage' in scores
        assert 'ats_score' in scores
        assert 'impact_density' in scores
        
        # Scores should be between 0 and 100
        for score_key in ['overall_score', 'keyword_coverage', 'ats_score', 'impact_density']:
            score = scores[score_key]
            assert 0 <= score <= 100

class TestAPIEndpoints:
    """Test Flask API endpoints"""
    
    @pytest.fixture
    def client(self):
        from src.routes.resume_routes import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_health_endpoint(self, client):
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'

    def test_analyze_endpoint_json(self, client):
        test_data = {
            'resume_text': SAMPLE_RESUME_TEXT,
            'job_description': SAMPLE_JOB_DESCRIPTION
        }
        
        response = client.post('/api/analyze', 
                             data=json.dumps(test_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'parsed_resume' in data
        assert 'scores' in data
        assert 'gaps' in data
        assert 'compliance_issues' in data

    def test_keywords_endpoint(self, client):
        test_data = {
            'job_description': SAMPLE_JOB_DESCRIPTION,
            'use_llm': False
        }
        
        response = client.post('/api/keywords',
                             data=json.dumps(test_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'keywords' in data
        assert len(data['keywords']) > 0

    def test_rewrite_bullets_endpoint(self, client):
        test_data = {
            'bullets': ['I worked on backend systems', 'Helped improve performance'],
            'job_description': SAMPLE_JOB_DESCRIPTION,
            'tone': 'professional'
        }
        
        response = client.post('/api/rewrite-bullets',
                             data=json.dumps(test_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'rewrites' in data
        assert len(data['rewrites']) == 2

if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
