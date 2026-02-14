from pydantic import BaseModel
from typing import Optional


class AnalyzePostModel(BaseModel):
    role: Optional[str]
    experience: Optional[str]
    seniority: Optional[str]
    location: Optional[str]
    company: Optional[str]
    recruiter: Optional[str]
    recruiter_profile_link: Optional[str]
    email: Optional[str]
    needs_cv: Optional[bool]


class ScoreJobModel(BaseModel):
    score: int
    reason: str


class EmailModel(BaseModel):
    subject: str
    body: str


class LinkedInMessageModel(BaseModel):
    message: str
