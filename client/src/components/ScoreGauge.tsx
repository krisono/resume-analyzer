import React from "react";
import { CheckCircle, AlertTriangle, XCircle, Info } from "lucide-react";

interface ScoreGaugeProps {
  score: number;
  label: string;
  description?: string;
  size?: "sm" | "md" | "lg";
}

export const ScoreGauge: React.FC<ScoreGaugeProps> = ({
  score,
  label,
  description,
  size = "md",
}) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return "success";
    if (score >= 60) return "good";
    if (score >= 40) return "warning";
    return "danger";
  };

  const getScoreIcon = (score: number) => {
    if (score >= 80) return CheckCircle;
    if (score >= 60) return Info;
    if (score >= 40) return AlertTriangle;
    return XCircle;
  };

  const scoreColor = getScoreColor(score);
  const Icon = getScoreIcon(score);

  const sizeClasses = {
    sm: "w-16 h-16 text-lg",
    md: "w-24 h-24 text-2xl",
    lg: "w-32 h-32 text-3xl",
  };

  const progressRadius = size === "sm" ? 28 : size === "md" ? 40 : 52;
  const progressCircumference = 2 * Math.PI * progressRadius;
  const progressOffset =
    progressCircumference - (score / 100) * progressCircumference;

  return (
    <div className="flex flex-col items-center space-y-3">
      {/* Circular Progress */}
      <div className="relative">
        <svg
          className={`${sizeClasses[size]} transform -rotate-90`}
          viewBox="0 0 120 120"
        >
          {/* Background circle */}
          <circle
            cx="60"
            cy="60"
            r={progressRadius}
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            className="text-gray-200"
          />
          {/* Progress circle */}
          <circle
            cx="60"
            cy="60"
            r={progressRadius}
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={progressCircumference}
            strokeDashoffset={progressOffset}
            className={`transition-all duration-1000 ease-out ${
              scoreColor === "success"
                ? "text-success-500"
                : scoreColor === "good"
                ? "text-blue-500"
                : scoreColor === "warning"
                ? "text-warning-500"
                : "text-danger-500"
            }`}
          />
        </svg>

        {/* Score and Icon */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <Icon
            className={`w-5 h-5 mb-1 ${
              scoreColor === "success"
                ? "text-success-600"
                : scoreColor === "good"
                ? "text-blue-600"
                : scoreColor === "warning"
                ? "text-warning-600"
                : "text-danger-600"
            }`}
          />
          <span
            className={`font-bold ${
              scoreColor === "success"
                ? "text-success-700"
                : scoreColor === "good"
                ? "text-blue-700"
                : scoreColor === "warning"
                ? "text-warning-700"
                : "text-danger-700"
            }`}
          >
            {Math.round(score)}%
          </span>
        </div>
      </div>

      {/* Label and Description */}
      <div className="text-center">
        <h3 className="font-semibold text-gray-900">{label}</h3>
        {description && (
          <p className="text-sm text-gray-600 max-w-xs">{description}</p>
        )}
      </div>
    </div>
  );
};
