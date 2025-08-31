import React, { useState } from "react";

export function UploadPanel({ onAnalyzed }: { onAnalyzed: (r: any) => void }) {
  const [resumeText, setResumeText] = useState("");
  const [jdText, setJdText] = useState("");

  const analyze = async () => {
    const resp = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        resume_text: resumeText,
        job_description_text: jdText,
      }),
    });
    const data = await resp.json();
    data._inputs = { resume_text: resumeText, job_description_text: jdText };
    onAnalyzed(data);
  };

  return (
    <div style={{ display: "grid", gap: "0.75rem" }}>
      <textarea
        placeholder="Paste resume text"
        value={resumeText}
        onChange={(e) => setResumeText(e.target.value)}
        rows={8}
      />
      <textarea
        placeholder="Paste job description"
        value={jdText}
        onChange={(e) => setJdText(e.target.value)}
        rows={6}
      />
      <button onClick={analyze}>Analyze</button>
    </div>
  );
}
