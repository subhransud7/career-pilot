from pydantic import BaseModel, Field


class AnalysisResult(BaseModel):
    role: str | None = None
    experience: str | None = None
    seniority: str | None = None
    location: str | None = None
    company: str | None = None
    recruiter: str | None = None
    recruiter_profile_link: str | None = None
    email: str | None = None
    score: int = Field(ge=0, le=100)
