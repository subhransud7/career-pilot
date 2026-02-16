from app.core.logger import DailyLogger
from app.models import Lead, VisitedLink
from app.services.ingestion_service import IngestionService


class FakeFetch:
    def __init__(self):
        self.calls = 0

    def fetch(self, url: str) -> str:
        self.calls += 1
        return "Hiring Java Developer at Acme. Send resume to jobs@acme.com"


class FakeAnalysis:
    def __init__(self, score: int):
        self.score = score
        self.calls = 0

    def analyze_post(self, raw_text: str) -> dict:
        self.calls += 1
        return {
            "role": "Java Developer",
            "experience": "3+ years",
            "seniority": "Mid",
            "location": "Remote",
            "company": "Acme",
            "recruiter": "Sam",
            "recruiter_profile_link": "https://linkedin.com/in/sam",
            "email": "jobs@acme.com",
            "score": self.score,
        }


def test_duplicate_prevention_calls_llm_once(db_session, tmp_path):
    fetch = FakeFetch()
    analysis = FakeAnalysis(score=80)
    service = IngestionService(db_session, fetch, analysis, DailyLogger(root=str(tmp_path / "logs")))

    r1 = service.process_single_link("https://linkedin.com/posts/a?trk=1", "SEARCH")
    r2 = service.process_single_link("https://linkedin.com/posts/a?trk=2", "SEARCH")

    assert r1["status"] == "processed"
    assert r2["status"] == "skipped"
    assert analysis.calls == 1
    assert fetch.calls == 1
    assert db_session.query(VisitedLink).count() == 1


def test_score_threshold_reject_and_accept(db_session, tmp_path):
    low = IngestionService(db_session, FakeFetch(), FakeAnalysis(score=10), DailyLogger(root=str(tmp_path / "logs1")))
    low.process_single_link("https://linkedin.com/posts/low", "SEARCH")
    assert db_session.query(VisitedLink).count() == 1
    assert db_session.query(Lead).count() == 0

    high = IngestionService(db_session, FakeFetch(), FakeAnalysis(score=50), DailyLogger(root=str(tmp_path / "logs2")))
    high.process_single_link("https://linkedin.com/posts/high", "SEARCH")
    assert db_session.query(VisitedLink).count() == 2
    assert db_session.query(Lead).count() == 1


def test_ingestion_end_to_end_persists_metadata(db_session, tmp_path):
    svc = IngestionService(db_session, FakeFetch(), FakeAnalysis(score=70), DailyLogger(root=str(tmp_path / "logs3")))
    out = svc.process_single_link("https://linkedin.com/posts/end2end", "CSV")

    assert out["accepted"] is True
    visited = db_session.query(VisitedLink).first()
    lead = db_session.query(Lead).first()
    assert visited.source_type == "CSV"
    assert visited.processed is True
    assert visited.accepted is True
    assert lead.visited_link_id == visited.id
    assert lead.state == "IN_REVIEW"
