from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True)
    visited_link_id = Column(Integer, ForeignKey("visited_links.id", ondelete="RESTRICT"), nullable=False)
    post_link = Column(String, nullable=False)
    recruiter_profile_link = Column(String)
    raw_post = Column(Text)
    role = Column(String)
    experience = Column(String)
    seniority = Column(String)
    location = Column(String)
    company = Column(String)
    recruiter = Column(String)
    email = Column(String)
    keywords = Column(String)
    date_posted = Column(String)
    score = Column(Integer)
    state = Column(String, nullable=False, default="IN_REVIEW")
    mail_failure_reason = Column(Text)
    email_subject = Column(Text)
    email_body = Column(Text)
    linkedin_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    visited_link = relationship("VisitedLink")


Index("ix_leads_state", Lead.state)
Index("ix_leads_created_at", Lead.created_at)
