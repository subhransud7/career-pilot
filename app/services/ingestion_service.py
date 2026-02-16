from __future__ import annotations

from sqlalchemy.orm import Session
from app.core.logger import DailyLogger
from app.models import Lead
from app.repositories.leads import LeadsRepository
from app.repositories.visited_links import VisitedLinksRepository
from app.services.link_utils import normalize_link, hash_link


class IngestionService:
    def __init__(self, db: Session, fetch_service, analysis_service, logger: DailyLogger):
        self.db = db
        self.fetch_service = fetch_service
        self.analysis_service = analysis_service
        self.logger = logger
        self.visited_repo = VisitedLinksRepository(db)
        self.leads_repo = LeadsRepository(db)

    async def process_single_link(self, link: str, source_type: str, csv_date: str | None = None) -> dict:
        normalized = normalize_link(link)
        link_hash = hash_link(normalized)

        try:
            existing = self.visited_repo.get_by_hash(link_hash)
            if existing and existing.processed:
                if existing.accepted is False:
                    self.logger.run(f"skip_duplicate link_hash={link_hash} url={normalized}")
                    return {"status": "skipped", "reason": "duplicate", "link_hash": link_hash}

                if existing.accepted is True:
                    existing_lead = (
                        self.leads_repo.db.query(Lead)
                        .filter(Lead.visited_link_id == existing.id)
                        .first()
                    )
                    if existing_lead:
                        self.logger.run(f"skip_duplicate link_hash={link_hash} url={normalized}")
                        return {"status": "skipped", "reason": "duplicate", "link_hash": link_hash}
                    self.logger.run(f"recovery_missing_lead link_hash={link_hash}")
                    existing.processed = False

            self.logger.run(f"processing_link source={source_type} url={normalized}")

            raw_post = await self.fetch_service.fetch(normalized)
            analysis = self.analysis_service.analyze_post(raw_post)
            score = int(analysis.get("score", 0))
            accepted = score >= 5

            self.logger.llm({
                "url": normalized,
                "link_hash": link_hash,
                "source_type": source_type,
                "analysis": analysis,
            })
            self.logger.run(f"decision link_hash={link_hash} score={score} accepted={accepted}")

            if existing:
                visited = existing
                visited.original_url = link
                visited.normalized_url = normalized
                visited.source_type = source_type
                visited.processed = True
                visited.score = score
                visited.accepted = accepted
            else:
                visited = self.visited_repo.create(
                    original_url=link,
                    normalized_url=normalized,
                    link_hash=link_hash,
                    source_type=source_type,
                    processed=True,
                    score=score,
                    accepted=accepted,
                )

            lead_id = None
            if accepted:
                lead = self.leads_repo.create(
                    visited_link_id=visited.id,
                    post_link=normalized,
                    recruiter_profile_link=analysis.get("recruiter_profile_link"),
                    raw_post=raw_post,
                    role=analysis.get("role"),
                    experience=analysis.get("experience"),
                    seniority=analysis.get("seniority"),
                    location=analysis.get("location"),
                    company=analysis.get("company"),
                    recruiter=analysis.get("recruiter"),
                    email=analysis.get("email"),
                    keywords=analysis.get("keywords"),
                    date_posted=csv_date,
                    score=score,
                    state="IN_REVIEW",
                    email_subject=None,
                    email_body=None,
                    linkedin_message=None,
                )
                lead_id = lead.id

            self.db.commit()

            return {
                "status": "processed",
                "link_hash": link_hash,
                "accepted": accepted,
                "score": score,
                "lead_id": lead_id,
            }
        except Exception as exc:
            self.db.rollback()
            self.logger.error(
                f"ingestion_error original_url={link} normalized_url={normalized} "
                f"link_hash={link_hash} error={exc}"
            )
            raise
