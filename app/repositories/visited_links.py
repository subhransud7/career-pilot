from sqlalchemy.orm import Session
from app.models import VisitedLink


class VisitedLinksRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_hash(self, link_hash: str):
        return self.db.query(VisitedLink).filter(VisitedLink.link_hash == link_hash).first()

    def create(self, **kwargs) -> VisitedLink:
        row = VisitedLink(**kwargs)
        self.db.add(row)
        self.db.flush()
        return row

    def count(self) -> int:
        return self.db.query(VisitedLink).count()
