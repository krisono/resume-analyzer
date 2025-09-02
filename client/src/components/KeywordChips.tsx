import React from "react";
import { Tag, CheckCircle, XCircle } from "lucide-react";

interface KeywordChipsProps {
  keywords: Array<{
    keyword: string;
    in_resume: boolean;
    frequency?: number;
    context_snippets?: string[];
  }>;
  title?: string;
  maxDisplay?: number;
}

export const KeywordChips: React.FC<KeywordChipsProps> = ({
  keywords,
  title = "Keywords",
  maxDisplay = 20,
}) => {
  const displayKeywords = keywords.slice(0, maxDisplay);
  const remainingCount = keywords.length - maxDisplay;

  if (!keywords.length) return null;

  return (
    <div className="space-y-4">
      <h3 className="flex items-center space-x-2 text-lg font-semibold text-gray-900">
        <Tag className="w-5 h-5" />
        <span>{title}</span>
      </h3>

      <div className="flex flex-wrap gap-2">
        {displayKeywords.map((item, index) => (
          <div
            key={index}
            className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full text-sm font-medium border transition-all duration-200 hover:scale-105 ${
              item.in_resume
                ? "bg-success-50 text-success-800 border-success-200 hover:bg-success-100"
                : "bg-danger-50 text-danger-800 border-danger-200 hover:bg-danger-100"
            }`}
            title={
              item.in_resume
                ? `Found ${item.frequency || 1} time(s)`
                : "Not found in resume"
            }
          >
            {item.in_resume ? (
              <CheckCircle className="w-3 h-3" />
            ) : (
              <XCircle className="w-3 h-3" />
            )}
            <span>{item.keyword}</span>
            {item.in_resume && item.frequency && item.frequency > 1 && (
              <span className="bg-success-200 text-success-900 text-xs px-1.5 py-0.5 rounded-full ml-1">
                {item.frequency}
              </span>
            )}
          </div>
        ))}
      </div>

      {remainingCount > 0 && (
        <p className="text-sm text-gray-600">
          And {remainingCount} more keywords...
        </p>
      )}

      {/* Summary Stats */}
      <div className="flex items-center space-x-4 text-sm text-gray-600">
        <div className="flex items-center space-x-1">
          <CheckCircle className="w-4 h-4 text-success-600" />
          <span>{keywords.filter((k) => k.in_resume).length} found</span>
        </div>
        <div className="flex items-center space-x-1">
          <XCircle className="w-4 h-4 text-danger-600" />
          <span>{keywords.filter((k) => !k.in_resume).length} missing</span>
        </div>
      </div>
    </div>
  );
};
