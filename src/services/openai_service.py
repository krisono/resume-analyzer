from __future__ import annotations
from typing import List
try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # type: ignore

class OpenAISuggester:
    def __init__(self, api_key: str | None):
        self.client = None
        self.enabled = False
        if api_key and OpenAI:
            try:
                self.client = OpenAI(api_key=api_key)
                self.enabled = True
            except Exception:
                self.client = None
                self.enabled = False

    def suggest(self, resume_text: str, jd_text: str) -> List[str]:
        if not self.enabled or not self.client:
            return []
        prompt = (
            "You are an expert resume reviewer. Given a resume and a job description, "
            "produce 5 concise, actionable improvement suggestions focused on ATS compliance, "
            "keyword alignment, and clarity. Return a numbered list.\n\n"
            f"RESUME:\n{resume_text[:6000]}\n\nJOB DESCRIPTION:\n{jd_text[:6000]}\n"
        )
        try:
            resp = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=300,
            )
            text = resp.choices[0].message.content or ""
            lines = [l.strip(" -•") for l in text.split("\n") if l.strip()]
            return lines[:5]
        except Exception:
            return []