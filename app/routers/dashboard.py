import re
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db_session
from app.core.logger import DailyLogger
from app.execution.processor import SequentialProcessor
from app.models import Lead, VisitedLink
from app.services.analysis_service import AnalysisService
from app.services.csv_service import parse_links_csv
from app.services.fetch_service import FetchService
from app.services.ingestion_service import IngestionService
from app.services.search_service import SearchService

router = APIRouter()
templates = Jinja2Templates(directory="app/ui/templates")


def build_processor(db: Session) -> SequentialProcessor:
    logger = DailyLogger()
    ingestion = IngestionService(db, FetchService(), AnalysisService(), logger)
    return SequentialProcessor(ingestion)


def gmail_status() -> str:
    token_file = get_settings().gmail_token_file
    try:
        with open(token_file, "r", encoding="utf-8"):
            return "Configured"
    except Exception:
        return "Missing Token"


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db_session)):
    total_leads = db.query(Lead).count()
    total_visited = db.query(VisitedLink).count()
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "total_leads": total_leads,
            "total_visited": total_visited,
            "gmail_status": gmail_status(),
        },
    )


@router.post("/run-search", response_class=HTMLResponse)
async def run_search(
    request: Request,
    keywords: str = Form(...),
    days: int = Form(...),
    max_results: int = Form(10),
    db: Session = Depends(get_db_session),
):
    processor = build_processor(db)
    # deterministic input expansion: fetch 2N, processor handles dedupe + threshold
    links = SearchService().search_linkedin_posts(keywords, days, max_results * 2)
    results = await processor.process_links(links[: max_results * 2], "SEARCH")
    accepted = sum(1 for r in results if r.get("accepted"))
    skipped = sum(1 for r in results if r.get("status") == "skipped")

    return templates.TemplateResponse(
        "partials/run_result.html",
        {
            "request": request,
            "processed": len(results),
            "accepted": accepted,
            "skipped": skipped,
        },
    )


@router.post("/upload-csv", response_class=HTMLResponse)
async def upload_csv(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db_session),
):
    content = await file.read()
    filename = file.filename or ""

    # Extract date from filename
    date_match = re.search(
        r"(\d{4}[-_]\d{2}[-_]\d{2})|(\d{2}[-_]\d{2}[-_]\d{4})",
        filename
    )

    extracted_date = None

    if date_match:
        raw_date = date_match.group(0)

        # Normalize separators
        raw_date = raw_date.replace("_", "-")

        # Handle DD-MM-YYYY
        if re.match(r"\d{2}-\d{2}-\d{4}", raw_date):
            extracted_date = datetime.strptime(raw_date, "%d-%m-%Y").strftime("%Y-%m-%d")

        # Handle YYYY-MM-DD
        elif re.match(r"\d{4}-\d{2}-\d{2}", raw_date):
            extracted_date = raw_date

    links = parse_links_csv(content)
    processor = build_processor(db)
    results = await processor.process_links(links, "CSV", csv_date=extracted_date)
    accepted = sum(1 for r in results if r.get("accepted"))
    skipped = sum(1 for r in results if r.get("status") == "skipped")

    return templates.TemplateResponse(
        "partials/run_result.html",
        {
            "request": request,
            "processed": len(results),
            "accepted": accepted,
            "skipped": skipped,
        },
    )
