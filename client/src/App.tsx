import React, { useState } from "react";
import { Navbar } from "./components/Navbar";
import { UploadArea } from "./components/UploadArea";
import { AnalysisResult } from "./components/AnalysisResult";
import { ThemeToggle } from "./components/ThemeToggle";

export default function App() {
  const [result, setResult] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleAnalyze = (data: any) => {
    setResult(data);
    setIsLoading(false);
  };

  const handleStartAnalysis = () => {
    setIsLoading(true);
    setResult(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!result ? (
          <div className="max-w-4xl mx-auto">
            <UploadArea
              onAnalyze={handleAnalyze}
              onStartAnalysis={handleStartAnalysis}
              isLoading={isLoading}
            />
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <button onClick={() => setResult(null)} className="btn-secondary">
                ← Analyze Another Resume
              </button>
              <ThemeToggle />
            </div>

            <AnalysisResult result={result} />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <p className="text-gray-600">
              Built by{" "}
              <a
                href="https://nnaemekaonochie.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary-600 hover:text-primary-700 font-medium"
              >
                Nnaemeka Onochie
              </a>
            </p>
            <p className="text-sm text-gray-500 mt-2">
              AI-powered resume analysis for better job applications
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
