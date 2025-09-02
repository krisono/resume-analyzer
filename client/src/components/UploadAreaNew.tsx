import React, { useState, useCallback } from "react";
import {
  Upload,
  FileText,
  Briefcase,
  Loader,
  AlertCircle,
  Sparkles,
  Zap,
  Target,
} from "lucide-react";

interface UploadAreaProps {
  onAnalyze: (data: any) => void;
  isLoading?: boolean;
}

export const UploadArea: React.FC<UploadAreaProps> = ({
  onAnalyze,
  isLoading = false,
}) => {
  const [resumeText, setResumeText] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState("");

  const handleAnalyze = useCallback(async () => {
    if (!resumeText.trim() || !jobDescription.trim()) {
      setError("Please provide both resume text and job description");
      return;
    }

    setError("");

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          resume_text: resumeText,
          job_description_text: jobDescription,
        }),
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      const result = await response.json();
      result._inputs = {
        resume_text: resumeText,
        job_description_text: jobDescription,
      };
      onAnalyze(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    }
  }, [resumeText, jobDescription, onAnalyze]);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);

      const files = e.dataTransfer.files;
      if (files && files[0]) {
        const file = files[0];
        const reader = new FileReader();
        reader.onload = (event) => {
          const text = event.target?.result as string;
          if (resumeText.trim() === "") {
            setResumeText(text);
          } else {
            setJobDescription(text);
          }
        };
        reader.readAsText(file);
      }
    },
    [resumeText]
  );

  const loadSampleData = () => {
    setResumeText(`John Doe
Software Engineer

📧 john.doe@email.com | 📱 (555) 123-4567 | 🔗 linkedin.com/in/johndoe | 💻 github.com/johndoe

PROFESSIONAL SUMMARY
Experienced Software Engineer with 5+ years developing scalable web applications using modern technologies. Proven track record of delivering high-quality solutions and leading cross-functional teams.

EXPERIENCE

Senior Software Engineer | Tech Corp | 2020 - Present
• Developed and maintained 15+ microservices using Python, Django, and FastAPI
• Led a team of 4 developers in delivering critical features ahead of schedule
• Implemented CI/CD pipelines that reduced deployment time by 60%
• Optimized database queries resulting in 40% performance improvement
• Collaborated with product managers and designers on user experience enhancements

Software Developer | StartupXYZ | 2018 - 2020
• Built REST APIs serving 100K+ daily active users using Node.js and Express
• Implemented real-time features using WebSocket and Redis
• Worked with PostgreSQL and MongoDB for data storage solutions
• Developed automated testing suite achieving 95% code coverage
• Participated in code reviews and mentored junior developers

EDUCATION
Bachelor of Science in Computer Science | University of Technology | 2014 - 2018
• Relevant Coursework: Data Structures, Algorithms, Database Systems, Software Engineering

TECHNICAL SKILLS
Languages: Python, JavaScript, TypeScript, Java, SQL
Frameworks: React, Django, FastAPI, Node.js, Express, Spring Boot
Databases: PostgreSQL, MongoDB, Redis, MySQL
Tools: Git, Docker, Kubernetes, AWS, Jenkins, Jira
Testing: Jest, PyTest, Selenium, Postman

PROJECTS
E-commerce Platform: Built full-stack e-commerce solution with React frontend and Python backend
Task Management App: Developed collaborative project management tool with real-time updates
Data Analytics Dashboard: Created interactive dashboard for business intelligence using D3.js`);

    setJobDescription(`Senior Full Stack Developer - Remote

🚀 Join our innovative team building the next generation of financial technology solutions!

ABOUT THE ROLE
We're seeking a talented Senior Full Stack Developer to join our growing engineering team. You'll be responsible for developing and maintaining our core platform that serves millions of users worldwide.

WHAT YOU'LL DO
• Design and develop scalable web applications using modern technologies
• Collaborate with cross-functional teams to deliver high-quality features
• Mentor junior developers and contribute to technical decision-making
• Optimize application performance and ensure security best practices
• Participate in code reviews and maintain high coding standards
• Work in an agile environment with continuous integration and deployment

REQUIRED QUALIFICATIONS
• 5+ years of experience in full-stack development
• Strong proficiency in Python and modern frameworks (Django, FastAPI, Flask)
• Experience with JavaScript/TypeScript and React ecosystem
• Solid understanding of database design and optimization (PostgreSQL, MongoDB)
• Experience with cloud platforms (AWS, GCP, or Azure)
• Knowledge of containerization and orchestration (Docker, Kubernetes)
• Familiarity with CI/CD pipelines and DevOps practices
• Experience with version control systems (Git)
• Strong problem-solving skills and attention to detail

PREFERRED QUALIFICATIONS
• Experience with microservices architecture
• Knowledge of message queues and event-driven systems
• Familiarity with Redis and caching strategies
• Experience with automated testing frameworks
• Understanding of security best practices
• Previous experience in fintech or similar regulated industries
• Bachelor's degree in Computer Science or equivalent experience

TECHNICAL STACK
• Backend: Python, Django, FastAPI, PostgreSQL, Redis
• Frontend: React, TypeScript, Next.js, Tailwind CSS
• Infrastructure: AWS, Docker, Kubernetes, Jenkins
• Monitoring: Datadog, Sentry, CloudWatch

WHAT WE OFFER
• Competitive salary: $130,000 - $160,000
• Comprehensive health, dental, and vision insurance
• Flexible remote work arrangements
• Professional development budget ($2,000/year)
• Stock options and performance bonuses
• 25 days PTO + holidays
• Modern equipment and home office stipend`);
  };

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-6">
        <div className="inline-flex items-center space-x-2 bg-gradient-to-r from-blue-100 to-purple-100 px-4 py-2 rounded-full text-sm font-medium text-blue-800 border border-blue-200">
          <Sparkles className="w-4 h-4" />
          <span>AI-Powered Resume Analysis</span>
        </div>

        <h1 className="text-4xl md:text-6xl font-bold text-gray-900 leading-tight">
          Optimize Your Resume for
          <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            {" "}
            Success
          </span>
        </h1>

        <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
          Get instant AI-powered insights on ATS compatibility, keyword
          optimization, and semantic alignment. Transform your resume into a
          job-winning document with our advanced analysis engine.
        </p>

        {/* Feature Pills */}
        <div className="flex flex-wrap justify-center gap-3 mt-6">
          <div className="flex items-center space-x-2 bg-white border border-gray-200 rounded-full px-4 py-2 shadow-sm">
            <Zap className="w-4 h-4 text-yellow-500" />
            <span className="text-sm font-medium text-gray-700">
              Instant Analysis
            </span>
          </div>
          <div className="flex items-center space-x-2 bg-white border border-gray-200 rounded-full px-4 py-2 shadow-sm">
            <Target className="w-4 h-4 text-green-500" />
            <span className="text-sm font-medium text-gray-700">
              ATS Compatible
            </span>
          </div>
          <div className="flex items-center space-x-2 bg-white border border-gray-200 rounded-full px-4 py-2 shadow-sm">
            <Sparkles className="w-4 h-4 text-purple-500" />
            <span className="text-sm font-medium text-gray-700">
              AI Suggestions
            </span>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 animate-fade-in">
          <div className="flex items-center space-x-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
            <p className="text-red-800 font-medium">{error}</p>
          </div>
        </div>
      )}

      {/* Main Input Section */}
      <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
        <div className="p-8">
          {/* Quick Start Button */}
          <div className="text-center mb-6">
            <button
              onClick={loadSampleData}
              className="inline-flex items-center space-x-2 text-blue-600 hover:text-blue-700 font-medium text-sm bg-blue-50 hover:bg-blue-100 px-4 py-2 rounded-lg transition-colors duration-200"
            >
              <Sparkles className="w-4 h-4" />
              <span>Try with Sample Data</span>
            </button>
          </div>

          {/* Input Areas */}
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Resume Input */}
            <div className="space-y-4">
              <label className="flex items-center space-x-3 text-lg font-semibold text-gray-800">
                <div className="flex items-center justify-center w-8 h-8 bg-blue-100 rounded-lg">
                  <FileText className="w-4 h-4 text-blue-600" />
                </div>
                <span>Your Resume</span>
              </label>

              <div
                className={`relative border-2 border-dashed rounded-xl transition-all duration-200 ${
                  dragActive
                    ? "border-blue-400 bg-blue-50"
                    : "border-gray-300 hover:border-gray-400"
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <textarea
                  className="w-full h-64 p-6 border-0 bg-transparent resize-none focus:outline-none focus:ring-0 text-gray-700 placeholder-gray-400"
                  placeholder="Paste your resume content here or drag & drop a text file..."
                  value={resumeText}
                  onChange={(e) => setResumeText(e.target.value)}
                  disabled={isLoading}
                />

                {dragActive && (
                  <div className="absolute inset-0 bg-blue-50 bg-opacity-90 border-2 border-dashed border-blue-400 rounded-xl flex items-center justify-center">
                    <div className="text-center">
                      <Upload className="w-12 h-12 text-blue-600 mx-auto mb-3" />
                      <p className="text-blue-700 font-semibold text-lg">
                        Drop your file here
                      </p>
                      <p className="text-blue-600 text-sm">
                        Supports .txt, .pdf, .docx files
                      </p>
                    </div>
                  </div>
                )}
              </div>

              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-500">
                  {resumeText.length} characters
                </span>
                <span className="text-gray-400">
                  • Tip: Include all sections (experience, skills, education)
                </span>
              </div>
            </div>

            {/* Job Description Input */}
            <div className="space-y-4">
              <label className="flex items-center space-x-3 text-lg font-semibold text-gray-800">
                <div className="flex items-center justify-center w-8 h-8 bg-purple-100 rounded-lg">
                  <Briefcase className="w-4 h-4 text-purple-600" />
                </div>
                <span>Job Description</span>
              </label>

              <textarea
                className="w-full h-64 p-6 border-2 border-gray-300 rounded-xl focus:border-purple-400 focus:ring-4 focus:ring-purple-100 transition-all duration-200 resize-none text-gray-700 placeholder-gray-400"
                placeholder="Paste the job description you're targeting..."
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                disabled={isLoading}
              />

              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-500">
                  {jobDescription.length} characters
                </span>
                <span className="text-gray-400">
                  • Tip: Include requirements and responsibilities
                </span>
              </div>
            </div>
          </div>

          {/* Analyze Button */}
          <div className="text-center mt-8">
            <button
              onClick={handleAnalyze}
              disabled={
                isLoading || !resumeText.trim() || !jobDescription.trim()
              }
              className="inline-flex items-center space-x-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none min-w-[200px]"
            >
              {isLoading ? (
                <>
                  <Loader className="w-6 h-6 animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-6 h-6" />
                  <span>Analyze Resume</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Bottom Tips Section */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 px-8 py-6 border-t border-gray-100">
          <h3 className="font-semibold text-gray-900 mb-3 text-center">
            💡 Get the Best Results
          </h3>
          <div className="grid md:grid-cols-3 gap-4 text-sm">
            <div className="text-center">
              <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                <FileText className="w-4 h-4 text-blue-600" />
              </div>
              <p className="text-gray-700">
                <strong>Complete Resume:</strong> Include all sections like
                experience, education, and skills
              </p>
            </div>
            <div className="text-center">
              <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                <Target className="w-4 h-4 text-purple-600" />
              </div>
              <p className="text-gray-700">
                <strong>Detailed Job Post:</strong> Provide full requirements
                and responsibilities
              </p>
            </div>
            <div className="text-center">
              <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                <Sparkles className="w-4 h-4 text-green-600" />
              </div>
              <p className="text-gray-700">
                <strong>Clear Format:</strong> Use clean, readable text without
                special formatting
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
