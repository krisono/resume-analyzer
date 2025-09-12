import React, { useState } from "react";
import {
  Download,
  FileText,
  Briefcase,
  Settings,
  Loader,
  CheckCircle,
  Palette,
  Code,
  User,
} from "lucide-react";

interface ResumeGeneratorProps {
  analysisResult: any;
}

interface ResumeData {
  contact: {
    name: string;
    email: string;
    phone: string;
    location: string;
  };
  summary: string;
  skills: string[];
  experience: Array<{
    company: string;
    role: string;
    start: string;
    end: string;
    bullets: string[];
  }>;
  projects: Array<{
    name: string;
    description: string;
    technologies: string[];
    link?: string;
  }>;
  education: Array<{
    school: string;
    degree: string;
    grad: string;
  }>;
  certifications: string[];
  links: {
    linkedin?: string;
    github?: string;
    portfolio?: string;
  };
}

export const ResumeGenerator: React.FC<ResumeGeneratorProps> = ({
  analysisResult,
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState("plain");
  const [selectedFormat, setSelectedFormat] = useState("pdf");
  const [showSuccess, setShowSuccess] = useState(false);

  // Extract resume data from analysis result or use defaults
  const getResumeData = (): ResumeData => {
    // This would ideally parse the resume text from the analysis
    // For now, we'll create a template that can be customized
    return {
      contact: {
        name: "Your Name",
        email: "your.email@example.com",
        phone: "(555) 123-4567",
        location: "City, State",
      },
      summary: analysisResult?.summary || "Professional summary based on your resume and the target job description.",
      skills: analysisResult?.missing_keywords?.slice(0, 10) || [
        "Python", "JavaScript", "React", "Node.js", "SQL"
      ],
      experience: [
        {
          company: "Your Current Company",
          role: "Your Current Role",
          start: "2022-01",
          end: "Present",
          bullets: [
            "Improved system efficiency by 40% through optimization",
            "Led team of 5 developers on critical projects",
            "Implemented new technologies resulting in faster delivery"
          ]
        }
      ],
      projects: [
        {
          name: "Notable Project",
          description: "Brief description of your key project",
          technologies: ["React", "Python", "PostgreSQL"],
          link: "https://github.com/yourusername/project"
        }
      ],
      education: [
        {
          school: "Your University",
          degree: "Bachelor of Science in Computer Science",
          grad: "2020"
        }
      ],
      certifications: ["AWS Certified Developer", "Certified Scrum Master"],
      links: {
        linkedin: "https://linkedin.com/in/yourprofile",
        github: "https://github.com/yourusername",
        portfolio: "https://yourportfolio.com"
      }
    };
  };

  const handleGenerateResume = async () => {
    setIsGenerating(true);
    setShowSuccess(false);

    try {
      const resumeData = getResumeData();
      
      const response = await fetch("https://resume-analyzer-ruddy-theta.vercel.app/api/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          resume_data: resumeData,
          template: selectedTemplate,
          format: selectedFormat,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to generate resume: ${response.statusText}`);
      }

      // Download the generated file
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `ats-optimized-resume-${selectedTemplate}.${selectedFormat}`;
      a.click();
      URL.revokeObjectURL(url);

      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
    } catch (error) {
      console.error("Error generating resume:", error);
      alert("Failed to generate resume. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  const templates = [
    {
      id: "plain",
      name: "Plain ATS",
      description: "Ultra-clean format optimized for ATS scanning",
      icon: FileText,
      preview: "Simple, professional layout with clear sections"
    },
    {
      id: "compact",
      name: "Compact",
      description: "Space-efficient design for extensive experience",
      icon: Briefcase,
      preview: "Condensed format that fits more content"
    },
    {
      id: "engineer",
      name: "Engineer",
      description: "Technical-focused template with skills prominence",
      icon: Code,
      preview: "Skills-first layout ideal for technical roles"
    }
  ];

  const formats = [
    { id: "pdf", name: "PDF", icon: FileText, description: "Best for applications" },
    { id: "docx", name: "DOCX", icon: FileText, description: "Editable Word document" },
    { id: "html", name: "HTML", icon: Code, description: "Web preview format" }
  ];

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-gray-900 flex items-center">
            <Palette className="w-5 h-5 mr-2 text-primary-600" />
            Generate ATS-Optimized Resume
          </h3>
          <p className="text-gray-600 mt-1">
            Create a professionally formatted resume optimized for this job posting
          </p>
        </div>
        {showSuccess && (
          <div className="flex items-center text-green-600 bg-green-50 px-3 py-2 rounded-lg">
            <CheckCircle className="w-4 h-4 mr-2" />
            <span className="text-sm font-medium">Resume generated successfully!</span>
          </div>
        )}
      </div>

      {/* Template Selection */}
      <div className="mb-6">
        <h4 className="font-semibold text-gray-900 mb-3">Choose Template</h4>
        <div className="grid md:grid-cols-3 gap-4">
          {templates.map((template) => {
            const IconComponent = template.icon;
            return (
              <button
                key={template.id}
                onClick={() => setSelectedTemplate(template.id)}
                className={`p-4 border-2 rounded-lg text-left transition-all ${
                  selectedTemplate === template.id
                    ? "border-primary-500 bg-primary-50"
                    : "border-gray-200 hover:border-gray-300"
                }`}
              >
                <div className="flex items-center mb-2">
                  <IconComponent className="w-5 h-5 mr-2 text-primary-600" />
                  <span className="font-medium">{template.name}</span>
                </div>
                <p className="text-sm text-gray-600 mb-2">{template.description}</p>
                <p className="text-xs text-gray-500">{template.preview}</p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Format Selection */}
      <div className="mb-6">
        <h4 className="font-semibold text-gray-900 mb-3">Output Format</h4>
        <div className="flex gap-3">
          {formats.map((format) => {
            const IconComponent = format.icon;
            return (
              <button
                key={format.id}
                onClick={() => setSelectedFormat(format.id)}
                className={`flex items-center px-4 py-2 rounded-lg border-2 transition-all ${
                  selectedFormat === format.id
                    ? "border-primary-500 bg-primary-50 text-primary-700"
                    : "border-gray-200 hover:border-gray-300"
                }`}
              >
                <IconComponent className="w-4 h-4 mr-2" />
                <div className="text-left">
                  <div className="font-medium">{format.name}</div>
                  <div className="text-xs opacity-70">{format.description}</div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Generation Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div className="flex items-start">
          <Settings className="w-5 h-5 text-blue-600 mr-3 mt-0.5" />
          <div>
            <h5 className="font-medium text-blue-900">What's Included</h5>
            <ul className="text-sm text-blue-700 mt-2 space-y-1">
              <li>• ATS-optimized formatting and structure</li>
              <li>• Keywords from the job description integrated naturally</li>
              <li>• Professional bullet points enhanced with action verbs</li>
              <li>• Clean, readable layout that passes automated screening</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Generate Button */}
      <button
        onClick={handleGenerateResume}
        disabled={isGenerating}
        className="btn-primary w-full flex items-center justify-center space-x-2 disabled:opacity-50"
      >
        {isGenerating ? (
          <>
            <Loader className="w-5 h-5 animate-spin" />
            <span>Generating Resume...</span>
          </>
        ) : (
          <>
            <Download className="w-5 h-5" />
            <span>Generate {selectedFormat.toUpperCase()} Resume</span>
          </>
        )}
      </button>

      <p className="text-xs text-gray-500 text-center mt-3">
        Note: Review and customize the generated resume before applying to jobs
      </p>
    </div>
  );
};
