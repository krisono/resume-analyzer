import React from "react";
import { Brain, Github, Globe } from "lucide-react";
import { useTheme } from "../theme/ThemeContext";

export const Navbar: React.FC = () => {
  const { theme, toggle } = useTheme();

  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Brand */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-10 h-10 bg-primary-600 rounded-lg">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div className="flex flex-col">
              <h1 className="text-xl font-bold text-gray-900">
                Resume Analyzer
              </h1>
              <p className="text-sm text-gray-500">
                AI-Powered ATS & Keyword Analysis
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-6">
            <a
              href="https://nnaemekaonochie.com"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-2 text-gray-600 hover:text-primary-600 transition-colors duration-200"
            >
              <Globe className="w-4 h-4" />
              <span>Portfolio</span>
            </a>

            <a
              href="https://github.com/krisono/resume-analyzer"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-2 text-gray-600 hover:text-primary-600 transition-colors duration-200"
            >
              <Github className="w-4 h-4" />
              <span>GitHub</span>
            </a>

            {/* Theme Toggle */}
            <button
              onClick={toggle}
              className="p-2 rounded-lg text-gray-600 hover:text-primary-600 hover:bg-gray-100 transition-all duration-200"
              aria-label="Toggle theme"
            >
              {theme === "light" ? "🌙" : "☀️"}
            </button>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              className="p-2 rounded-lg text-gray-600 hover:text-primary-600 hover:bg-gray-100"
              aria-label="Menu"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};
