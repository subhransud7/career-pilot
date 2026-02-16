from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func
from app.core.database import Base


class VisitedLink(Base):
    __tablename__ = "visited_links"

    id = Column(Integer, primary_key=True)
    original_url = Column(String, nullable=False)
    normalized_url = Column(String, nullable=False)
    link_hash = Column(String, nullable=False, unique=True, index=True)
    source_type = Column(String, nullable=False)  # SEARCH / CSV
    processed = Column(Boolean, nullable=False, default=False)
    score = Column(Integer)
    accepted = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
