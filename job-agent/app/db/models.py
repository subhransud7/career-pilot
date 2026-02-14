from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .database import Base

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    post_link = Column(String)
    recruiter_profile_link = Column(String)
    raw_post = Column(Text)

    role = Column(String)
    experience = Column(String)
    seniority = Column(String)
    location = Column(String)
    company = Column(String)
    recruiter = Column(String)
    email = Column(String)

    score = Column(Integer)
    score_reason = Column(Text)

    state = Column(String, default="NEW")

    email_subject = Column(Text)
    email_body = Column(Text)
    linkedin_message = Column(Text)

    agent_used = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
