import React from "react";

export function ScoreCard({
  scores,
  summary,
}: {
  scores: any;
  summary: string;
}) {
  return (
    <div
      style={{
        border: "1px solid #ddd",
        padding: "1rem",
        borderRadius: 12,
        marginTop: "1rem",
      }}
    >
      <div>
        <strong>Summary:</strong> {summary}
      </div>
      <div style={{ display: "flex", gap: "1rem", marginTop: "0.5rem" }}>
        <span>ATS: {scores.ats_score}%</span>
        <span>Keywords: {scores.keyword_score}%</span>
        <span>Overall: {scores.overall_score}%</span>
      </div>
    </div>
  );
}
