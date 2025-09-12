import React from "react";
import {
  Download,
  FileText,
  TrendingUp,
  Target,
  Brain,
  CheckCircle,
  XCircle,
} from "lucide-react";
import { ScoreGauge } from "./ScoreGauge";
import { ResumeGenerator } from "./ResumeGenerator";

interface AnalysisResultProps {
  result: any;
}

export const AnalysisResult: React.FC<AnalysisResultProps> = ({ result }) => {
  const handleDownloadPDF = async () => {
    try {
      const response = await fetch("https://resume-analyzer-ruddy-theta.vercel.app/api/report/pdf", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          resume_text: result._inputs?.resume_text,
          job_description_text: result._inputs?.job_description_text,
        }),
      });

      if (!response.ok) throw new Error("Failed to generate PDF");

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "resume-analysis-report.pdf";
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading PDF:", error);
    }
  };

  const { scores, summary, missing_keywords, coverage, suggestions } = result;
  const atsChecks = scores?.checks || {};

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header with Summary */}
      <div className="card">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-900 mb-3">
              Analysis Results
            </h2>
            <p className="text-gray-700 leading-relaxed">{summary}</p>
          </div>
          <button
            onClick={handleDownloadPDF}
            className="btn-primary ml-4 flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Download PDF</span>
          </button>
        </div>
      </div>

      {/* Score Gauges */}
      <div className="grid md:grid-cols-3 gap-6">
        <div className="card text-center">
          <ScoreGauge
            score={scores?.ats_score || 0}
            label="ATS Compatibility"
            description="How well your resume passes Applicant Tracking Systems"
            size="lg"
          />
        </div>

        <div className="card text-center">
          <ScoreGauge
            score={scores?.keyword_score || 0}
            label="Keyword Match"
            description="Alignment between your skills and job requirements"
            size="lg"
          />
        </div>

        <div className="card text-center">
          <ScoreGauge
            score={scores?.overall_score || 0}
            label="Overall Score"
            description="Combined assessment of your resume's effectiveness"
            size="lg"
          />
        </div>
      </div>

      {/* ATS Checks */}
      <div className="card">
        <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
          <FileText className="w-5 h-5" />
          <span>ATS Compatibility Checks</span>
        </h3>
        <div className="grid md:grid-cols-2 gap-4">
          {Object.entries(atsChecks).map(([key, passed]) => (
            <div key={key} className="flex items-center space-x-3">
              {passed ? (
                <CheckCircle className="w-5 h-5 text-success-600" />
              ) : (
                <XCircle className="w-5 h-5 text-danger-600" />
              )}
              <span
                className={`font-medium ${
                  passed ? "text-success-700" : "text-danger-700"
                }`}
              >
                {key
                  .replace(/_/g, " ")
                  .replace(/\b\w/g, (l) => l.toUpperCase())}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Missing Keywords */}
      {missing_keywords && missing_keywords.length > 0 && (
        <div className="card">
          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
            <Target className="w-5 h-5" />
            <span>Missing Keywords</span>
          </h3>
          <div className="flex flex-wrap gap-2">
            {missing_keywords
              .slice(0, 20)
              .map((keyword: string, index: number) => (
                <span key={index} className="chip-warning">
                  {keyword}
                </span>
              ))}
          </div>
          {missing_keywords.length > 20 && (
            <p className="text-sm text-gray-600 mt-3">
              And {missing_keywords.length - 20} more keywords...
            </p>
          )}
        </div>
      )}

      {/* Keyword Coverage */}
      {coverage && coverage.length > 0 && (
        <div className="card">
          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
            <TrendingUp className="w-5 h-5" />
            <span>Keyword Analysis</span>
          </h3>
          <div className="space-y-3">
            {coverage.slice(0, 10).map((item: any, index: number) => (
              <div
                key={index}
                className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0"
              >
                <div className="flex items-center space-x-3">
                  <span
                    className={`chip ${
                      item.in_resume ? "chip-success" : "chip-danger"
                    }`}
                  >
                    {item.keyword}
                  </span>
                  {item.in_resume && (
                    <span className="text-sm text-gray-600">
                      Found {item.frequency} time(s)
                    </span>
                  )}
                </div>
                {item.in_resume ? (
                  <CheckCircle className="w-4 h-4 text-success-600" />
                ) : (
                  <XCircle className="w-4 h-4 text-danger-600" />
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Section Alignment */}
      {scores?.section_alignment && scores.section_alignment.length > 0 && (
        <div className="card">
          <h3 className="text-xl font-bold text-gray-900 mb-4">
            Section Alignment
          </h3>
          <div className="space-y-3">
            {scores.section_alignment.map((section: any, index: number) => (
              <div key={index} className="flex items-center justify-between">
                <span className="font-medium text-gray-700 capitalize">
                  {section.section}
                </span>
                <div className="flex items-center space-x-3">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-500 ${
                        section.similarity >= 80
                          ? "bg-success-500"
                          : section.similarity >= 60
                          ? "bg-blue-500"
                          : section.similarity >= 40
                          ? "bg-warning-500"
                          : "bg-danger-500"
                      }`}
                      style={{ width: `${Math.max(section.similarity, 5)}%` }}
                    />
                  </div>
                  <span className="font-semibold text-gray-900 min-w-[3rem] text-right">
                    {Math.round(section.similarity)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Suggestions */}
      {suggestions && suggestions.length > 0 && (
        <div className="card">
          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
            <Brain className="w-5 h-5" />
            <span>AI Suggestions</span>
          </h3>
          <div className="space-y-3">
            {suggestions.map((suggestion: string, index: number) => (
              <div
                key={index}
                className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg"
              >
                <div className="w-6 h-6 bg-blue-200 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-blue-700 text-sm font-semibold">
                    {index + 1}
                  </span>
                </div>
                <p className="text-blue-800">{suggestion}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Resume Generator Section */}
      <ResumeGenerator analysisResult={result} />
    </div>
  );
};
