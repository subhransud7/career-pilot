from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.database import Base, engine, SessionLocal
from app.db.models import Lead
from fastapi import Form
from fastapi.responses import RedirectResponse
from fastapi import Form
from app.tasks.aggregator import Aggregator


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/ui/static"), name="static")
templates = Jinja2Templates(directory="app/ui/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    total = db.query(Lead).count()
    new = db.query(Lead).filter(Lead.state == "NEW").count()
    mailed = db.query(Lead).filter(Lead.state == "MAILED").count()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "total": total,
        "new": new,
        "mailed": mailed
    })

@app.get("/review", response_class=HTMLResponse)
def review(
    request: Request,
    state: str = None,
    min_score: int = None,
    location: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Lead)

    if state:
        query = query.filter(Lead.state == state)

    if min_score:
        query = query.filter(Lead.score >= min_score)

    if location:
        query = query.filter(Lead.location.ilike(f"%{location}%"))

    leads = query.order_by(Lead.created_at.desc()).limit(100).all()

    return templates.TemplateResponse("review.html", {
        "request": request,
        "leads": leads
    })


@app.get("/lead/{lead_id}", response_class=HTMLResponse)
def lead_detail(lead_id: int, request: Request, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    return templates.TemplateResponse("lead_detail.html", {
        "request": request,
        "lead": lead
    })

@app.post("/lead/{lead_id}/update-state")
def update_state(
    lead_id: int,
    new_state: str = Form(...),
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if lead:
        lead.state = new_state
        db.commit()

    return RedirectResponse(url="/review", status_code=303)

@app.post("/aggregate")
def aggregate(
    keywords: str = Form(...),
    days: int = Form(...),
    max_results: int = Form(10),
    db: Session = Depends(get_db)
):
    aggregator = Aggregator(db)
    results = aggregator.run(keywords, days, max_results)

    return {"processed": len(results)}

from app.services.email_service import EmailService

@app.post("/lead/{lead_id}/send-email")
def send_email(lead_id: int, db: Session = Depends(get_db)):

    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if not lead or not lead.email:
        return {"error": "Invalid lead"}

    email_service = EmailService()
    email_service.send_email(
        to_email=lead.email,
        subject=lead.email_subject,
        body=lead.email_body
    )

    lead.state = "MAILED"
    db.commit()

    return {"status": "sent"}

from app.services.sheets_service import SheetsService

@app.post("/export-approved")
def export_approved(db: Session = Depends(get_db)):

    leads = db.query(Lead).filter(Lead.state == "APPROVED").all()

    service = SheetsService()
    service.export_leads("Job Agent Export", leads)

    return {"exported": len(leads)}
