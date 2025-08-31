from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class AnalyzeRequest(BaseModel):
    resume_text: Optional[str] = None
    job_description_text: Optional[str] = None

class KeywordMatch(BaseModel):
    keyword: str
    in_resume: bool
    frequency: int
    context_snippets: List[str] = Field(default_factory=list)

class SectionScore(BaseModel):
    section: str
    similarity: float
    missing_terms: List[str] = Field(default_factory=list)

class ScoreBreakdown(BaseModel):
    ats_score: float
    keyword_score: float
    overall_score: float
    checks: Dict[str, bool]
    section_alignment: List[SectionScore] | None = None

class AnalyzeResponse(BaseModel):
    summary: str
    missing_keywords: List[str]
    coverage: List[KeywordMatch]
    scores: ScoreBreakdown
    suggestions: List[str]