import React, { useState } from "react";
import { UploadPanel } from "./components/UploadPanel";
import { ScoreCard } from "./components/ScoreCard";
import { MissingList } from "./components/MissingList";
import { SectionAlignment } from "./components/SectionAlignment";

export default function App() {
  const [result, setResult] = useState<any>(null);

  return (
    <div style={{ maxWidth: 900, margin: "2rem auto", padding: "0 1rem" }}>
      <h1>Resume Analyzer</h1>
      <UploadPanel onAnalyzed={setResult} />
      {result && (
        <>
          <ScoreCard scores={result.scores} summary={result.summary} />
          <MissingList items={result.missing_keywords} />
          <SectionAlignment items={result.scores.section_alignment || []} />
          <a
            href="#"
            onClick={async (e) => {
              e.preventDefault();
              const resp = await fetch("/api/report/pdf", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  resume_text: result._inputs?.resume_text,
                  job_description_text: result._inputs?.job_description_text,
                }),
              });
              const blob = await resp.blob();
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "resume-analysis.pdf";
              a.click();
              URL.revokeObjectURL(url);
            }}
          >
            Download PDF
          </a>
        </>
      )}
    </div>
  );
}
