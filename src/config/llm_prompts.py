# LLM Prompts and Configuration for Resume Generator

# System prompts for different AI-powered features
LLM_PROMPTS = {
    
    # Keyword Extraction from Job Descriptions
    'extract_keywords': {
        'system': """You are an expert ATS (Applicant Tracking System) analyst and recruiter. 
Your job is to extract the most important skills, technologies, and requirements from job descriptions.
Focus on hard skills, specific technologies, certifications, and measurable requirements.
Avoid generic soft skills unless explicitly emphasized.""",
        
        'user': """Extract must-have and nice-to-have skills from this job description.
Return a JSON array with objects containing:
- term: the exact skill/technology name (preserve capitalization)
- category: one of [language, framework, database, cloud, tool, methodology, certification, soft_skill]
- importance: float 0-1 (1 = must-have, 0.7 = preferred, 0.5 = nice-to-have)
- context: brief explanation of how it's used in the role

Focus on technical requirements and avoid generic terms.

Job Description:
{job_description}

Return only valid JSON:""",
        
        'example_response': '''[
  {"term": "Python", "category": "language", "importance": 1.0, "context": "primary backend language"},
  {"term": "React", "category": "framework", "importance": 0.9, "context": "frontend development"},
  {"term": "PostgreSQL", "category": "database", "importance": 0.8, "context": "main database system"},
  {"term": "AWS", "category": "cloud", "importance": 0.7, "context": "cloud infrastructure"},
  {"term": "Docker", "category": "tool", "importance": 0.6, "context": "containerization"}
]'''
    },
    
    # Bullet Point Rewriting
    'rewrite_bullet': {
        'system': """You are a professional resume writer specializing in ATS optimization and quantified achievements.
Your goal is to rewrite bullet points using the CAR format: Context + Action + Result.
Always include metrics when possible and use strong action verbs.""",
        
        'user': """Rewrite this bullet point to be more impactful and ATS-friendly:

RULES:
1. Start with a strong action verb (Built, Led, Optimized, Developed, Implemented, etc.)
2. Include specific technologies mentioned in the job description when relevant
3. Add quantified results (numbers, percentages, time saved, users affected)
4. Keep under 25 words
5. Remove first-person pronouns (I, my, me)
6. Use past tense for previous roles, present tense for current role
7. Focus on business impact, not just tasks

Original bullet: {original_bullet}
Job context: {job_description}
Role context: {role_info}
Is current role: {is_current}

Rewritten bullet:""",
        
        'fallback_rules': [
            "Start with action verb if missing",
            "Remove first-person pronouns", 
            "Add metrics if numbers are present",
            "Use consistent tense",
            "Keep technical terms from job description"
        ]
    },
    
    # Professional Summary Generation
    'generate_summary': {
        'system': """You are an expert resume writer who creates compelling professional summaries.
Focus on the candidate's top skills that match the job requirements and quantify experience when possible.""",
        
        'user': """Write a professional summary (2-3 sentences, max 50 words) that emphasizes the top 5 skills from the job description.

REQUIREMENTS:
- No first-person pronouns (I, my, me)
- Include years of experience if mentioned in resume
- Emphasize technical skills that match job requirements
- Include quantified achievements if available
- Professional tone appropriate for the industry

Resume data: {resume_data}
Job requirements: {job_description}
Industry: {industry}

Professional Summary:""",
        
        'example': "Full-stack engineer with 5+ years building scalable web applications using Python, React, and AWS. Led teams of 4+ developers and improved system performance by 40% serving 100K+ users."
    },
    
    # Skills Gap Analysis
    'analyze_gaps': {
        'system': """You are an ATS optimization expert who identifies missing skills and provides strategic advice.""",
        
        'user': """Analyze the gaps between this resume and job requirements. Provide actionable recommendations.

Resume skills: {resume_skills}
Job requirements: {job_requirements}
Resume experience: {resume_experience}

Provide JSON response with:
- critical_gaps: skills that are must-haves but missing
- skill_suggestions: how to position existing experience to cover gaps
- learning_priorities: top 3 skills to learn/emphasize
- positioning_advice: how to reframe existing experience

Response:""",
        
        'fallback_analysis': [
            "Compare skill lists directly",
            "Identify technology families (React/Angular/Vue)",
            "Look for transferable experience",
            "Prioritize by frequency in job description"
        ]
    },
    
    # Content Enhancement Suggestions
    'enhance_content': {
        'system': """You are a career coach specializing in resume optimization for specific job applications.""",
        
        'user': """Suggest specific improvements for this resume section to better match the job requirements:

Section: {section_type}
Current content: {current_content}
Job requirements: {job_requirements}
Target role level: {role_level}

Provide 3-5 specific, actionable suggestions for improvement:""",
        
        'guidelines': [
            "Be specific about what to add/change",
            "Reference exact job requirements",
            "Suggest quantifiable improvements",
            "Consider ATS keyword optimization",
            "Maintain professional authenticity"
        ]
    },
    
    # Company/Role Context Analysis
    'analyze_company_context': {
        'system': """You are a career strategist who understands company culture and role expectations.""",
        
        'user': """Analyze this job posting to understand the company culture, role expectations, and key success factors:

Job posting: {job_posting}
Company: {company_name}

Provide insights on:
- company_culture: startup vs enterprise, technical focus, etc.
- role_emphasis: what they value most (leadership, technical depth, etc.)  
- success_metrics: how success is likely measured
- language_style: formal vs casual, technical vs business-focused
- key_differentiators: what would make a candidate stand out

Use this to guide resume customization recommendations."""
    }
}

# Fallback heuristics when LLM is not available
FALLBACK_HEURISTICS = {
    'keyword_extraction': {
        'technical_patterns': [
            r'\b(Python|Java|JavaScript|TypeScript|React|Angular|Vue|Node\.js)\b',
            r'\b(Django|Flask|Spring|Express|Laravel|Rails)\b',
            r'\b(PostgreSQL|MySQL|MongoDB|Redis|Elasticsearch)\b',
            r'\b(AWS|Azure|GCP|Docker|Kubernetes|Jenkins)\b',
            r'\b(Git|Linux|CI/CD|DevOps|Agile|Scrum)\b'
        ],
        'skill_categories': {
            'languages': ['Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust'],
            'frameworks': ['React', 'Angular', 'Vue', 'Django', 'Flask', 'Spring', 'Express'],
            'databases': ['PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Cassandra'],
            'cloud': ['AWS', 'Azure', 'GCP', 'Heroku', 'Vercel'],
            'tools': ['Docker', 'Kubernetes', 'Jenkins', 'Git', 'Terraform']
        }
    },
    
    'bullet_improvement': {
        'action_verbs': [
            'Developed', 'Built', 'Created', 'Designed', 'Implemented',
            'Led', 'Managed', 'Directed', 'Coordinated', 'Supervised',
            'Optimized', 'Improved', 'Enhanced', 'Streamlined', 'Automated',
            'Delivered', 'Achieved', 'Exceeded', 'Reduced', 'Increased'
        ],
        'weak_phrases': [
            'worked on', 'helped with', 'was responsible for', 'participated in',
            'assisted in', 'involved in', 'contributed to', 'supported'
        ],
        'metric_patterns': [
            r'\d+%', r'\$\d+', r'\d+K', r'\d+M', r'\d+x', r'\d+ hours?',
            r'\d+ days?', r'\d+ weeks?', r'\d+ months?', r'\d+ users?'
        ]
    }
}

# Configuration for different AI providers
AI_CONFIG = {
    'openai': {
        'model': 'gpt-3.5-turbo',
        'max_tokens': 500,
        'temperature': 0.1,
        'timeout': 30
    },
    'anthropic': {
        'model': 'claude-3-haiku-20240307',
        'max_tokens': 500,
        'temperature': 0.1
    },
    'local': {
        'model': 'llama2',  # For local deployment
        'context_length': 2048
    }
}

# Quality control prompts
QUALITY_PROMPTS = {
    'validate_output': """Check if this resume bullet point is professional and accurate:
    
    Bullet: {bullet}
    
    Issues to check:
    - Professional language
    - No exaggeration or false claims
    - Proper grammar and tense
    - Specific and quantified when possible
    - ATS-friendly formatting
    
    Return: PASS or list specific issues to fix.""",
    
    'fact_check': """Verify this resume content doesn't contain any fabricated information:
    
    Content: {content}
    Original context: {original_context}
    
    Ensure:
    - No invented companies, roles, or dates
    - No exaggerated metrics beyond reasonable interpretation
    - Skills match demonstrated experience
    - Accomplishments are realistic for role/timeframe
    
    Assessment:"""
}

# Usage examples and test cases
EXAMPLE_USAGE = {
    'keyword_extraction_input': """
    Senior Full Stack Developer Position
    
    We're looking for a Senior Full Stack Developer with 5+ years of experience building scalable web applications. 
    
    Required Skills:
    - Python (Django/Flask)
    - React.js or Angular
    - PostgreSQL or MySQL
    - AWS (EC2, S3, RDS)
    - Docker containerization
    - RESTful API development
    - Git version control
    
    Preferred:
    - Kubernetes orchestration
    - Redis caching
    - GraphQL
    - CI/CD pipelines
    - Agile/Scrum methodology
    """,
    
    'bullet_rewrite_input': {
        'original': "Worked on the backend API using Python",
        'job_context': "Senior Backend Engineer - Python, Django, PostgreSQL, Redis, 1M+ users",
        'role_info': "Backend Engineer at TechCorp, 2022-Present",
        'is_current': True
    },
    
    'expected_output': "Develops scalable REST APIs using Python/Django serving 1M+ users with Redis caching integration"
}
