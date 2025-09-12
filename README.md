# Resume Analyzer - AI-Powered ATS & Keyword Analysis

<div align="center">

![Resume Analyzer](https://img.shields.io/badge/Resume-Analyzer-blue?style=for-the-badge&logo=brain)
![AI Powered](https://img.shields.io/badge/AI-Powered-green?style=for-the-badge)
![Full Stack](https://img.shields.io/badge/Full-Stack-orange?style=for-the-badge)

**A comprehensive full-stack application that evaluates resumes for ATS compatibility and keyword alignment with job descriptions using advanced NLP and machine learning techniques.**

[🚀 Live Demo](https://nnaemekaonochie.com/resume-analyzer) • [📖 Documentation](#documentation) • [🛠️ Installation](#installation)

</div>

## ✨ Features

### 🎯 **Core Analysis**

- **Multi-format Support**: Parse .pdf, .docx, and .txt files seamlessly
- **Advanced NLP**: Semantic similarity analysis using sentence transformers
- **Keyword Intelligence**: TF-IDF-based keyword extraction and coverage analysis
- **ATS Compatibility**: Comprehensive checks for formatting, structure, and readability
- **Named Entity Recognition**: Extract skills, technologies, and certifications
- **Scoring System**: Detailed breakdown of ATS score, keyword score, and overall rating

### 🎨 **UI/UX**

- **Responsive Design**: Beautiful, mobile-first interface built with Tailwind CSS
- **Interactive Components**: Animated score gauges, progress indicators, and smooth transitions
- **Dark/Light Theme**: Toggle between themes for optimal viewing experience
- **Real-time Feedback**: Instant visual feedback during analysis process
- **Accessibility**: WCAG compliant with proper ARIA labels and keyboard navigation

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**

### Backend Setup

```bash
# Clone and setup Python environment
git clone https://github.com/krisono/resume-analyzer.git
cd resume-analyzer
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies and download NLP models
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Environment configuration
cp .env.example .env
# Edit .env to add your OPENAI_API_KEY (optional)

# Start backend server
python run.py
```

### Frontend Setup

```bash
# In a new terminal, setup and start frontend
cd client
npm install
npm run dev
```

### 🌐 Access Points

- **Frontend**: http://localhost:5174
- **Backend API**: http://localhost:3001

## 📖 API Usage

### Authentication Endpoints

```bash
# Register new user
curl -X POST http://localhost:3001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'

# Login and get tokens
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

### Analysis Endpoints

```bash
# Authenticated analysis (saves to history)
curl -X POST http://localhost:3001/api/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "resume_text": "Software Engineer with Java and Python experience...",
    "job_description_text": "We need a Java backend developer with Spring Boot, Kafka..."
  }'

# Anonymous analysis (no history)
curl -X POST http://localhost:3001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Software Engineer...",
    "job_description_text": "Java developer needed..."
  }'

# File upload analysis
curl -X POST http://localhost:3001/api/analyze \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F resume=@resume.pdf \
  -F job_description=@job_description.txt

# Get analysis history
curl -X GET http://localhost:3001/api/analyze-history \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Download PDF report
curl -X POST http://localhost:3001/api/report/pdf \
  -H "Content-Type: application/json" \
  -d '{"resume_text":"...","job_description_text":"..."}' \
  --output analysis-report.pdf
```

## 🛠️ Installation

### Development Environment

```bash
# Complete setup for development
git clone https://github.com/krisono/resume-analyzer.git
cd resume-analyzer

# Backend setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Frontend setup (in new terminal)
cd client
npm install

# Start both servers
# Terminal 1: Backend
source .venv/bin/activate && python run.py

# Terminal 2: Frontend
cd client && npm run dev
```

### Production Deployment (Vercel)

```bash
# Deploy to Vercel
npm install -g vercel
vercel --prod

# Or use GitHub integration
git push origin main  # Auto-deploys via Vercel GitHub app
```

## 🎯 How It Works

### Analysis Pipeline

1. **Text Extraction**: Parse resumes from multiple formats
2. **NLP Processing**: Extract keywords, entities, and sections
3. **Semantic Analysis**: Calculate similarity between resume and job description
4. **ATS Evaluation**: Check formatting and structure compatibility
5. **Scoring**: Generate comprehensive scores and recommendations
6. **Reporting**: Provide detailed insights and improvement suggestions

### Key Algorithms

- **TF-IDF Vectorization**: For keyword importance calculation
- **Sentence Transformers**: For semantic similarity analysis
- **Named Entity Recognition**: For skill and technology extraction
- **Fuzzy String Matching**: For keyword variant detection

## 📊 Example Response

```json
{
  "summary": "Keyword coverage: 65.3%. ATS checks: 87.5%. Section alignment avg: 72%. Overall: 71.2%.",
  "scores": {
    "overall_score": 71.2,
    "keyword_score": 65.3,
    "ats_score": 87.5,
    "checks": {
      "has_sections": true,
      "has_contact_info": true,
      "reasonable_length": true,
      "bullet_usage": true
    }
  },
  "missing_keywords": ["kubernetes", "docker", "microservices"],
  "enhanced_features": {
    "semantic_similarity": 0.78,
    "entities": {
      "skills": ["Python", "React", "JavaScript"],
      "technologies": ["Flask", "PostgreSQL"]
    }
  },
  "suggestions": [
    "Add more specific technology keywords",
    "Include quantifiable achievements",
    "Improve section organization"
  ]
}
```

### Portfolio Features

- **Project Showcase**: Highlight as a featured full-stack project
- **Technical Skills**: Demonstrates AI/ML, full-stack development
- **User Value**: Practical tool for visitors and job seekers
- **SEO Benefits**: Increases site engagement and return visits

## 🧪 Testing

```bash
# Run comprehensive tests
python test_complete.py

# Run specific test suites
pytest tests/

# Frontend testing
cd client && npm test
```


## 👨‍💻 Author

**Nnaemeka Onochie**

- Portfolio: [nnaemekaonochie.com](https://nnaemekaonochie.com)
- GitHub: [@krisono](https://github.com/krisono)
- LinkedIn: [Nnaemeka Onochie](https://linkedin.com/in/nnaemeka-onochie)

---

<div align="center">

[🚀 Try it Live](resume-analyzer-git-main-nnaemekas-projects-510abf34.vercel.app) • [📧 Contact](mailto:kristopheronochie2@gmail.com)

</div>
