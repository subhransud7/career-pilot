from sqlalchemy.orm import Session
from app.models import Lead


class LeadsRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> Lead:
        row = Lead(**kwargs)
        self.db.add(row)
        self.db.flush()
        return row

    def list(self, state: str | None = None):
        query = self.base_query(state=state)
        return query.order_by(Lead.created_at.desc()).all()

    def base_query(self, state: str | None = None):
        query = self.db.query(Lead)
        if state:
            query = query.filter(Lead.state == state)
        return query

    def get(self, lead_id: int):
        return self.db.query(Lead).filter(Lead.id == lead_id).first()

    def approved(self):
        return self.db.query(Lead).filter(Lead.state == "APPROVED").order_by(Lead.created_at.desc()).all()
