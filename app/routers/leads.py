from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
from app.core.database import get_db_session
from app.core.errors import MailTokenError
from app.core.state_machine import LeadStateMachine
from app.models import Lead
from app.repositories.leads import LeadsRepository
from app.services.draft_service import DraftService
from app.services.mail_service import GmailMailService

router = APIRouter(prefix="/leads")
templates = Jinja2Templates(directory="app/ui/templates")


def score_class(score: int | None) -> str:
    if score is None:
        return "secondary"
    if score >= 70:
        return "success"
    if score >= 40:
        return "warning"
    return "danger"


@router.get("", response_class=HTMLResponse)
def list_leads(
    request: Request,
    state: str | None = None,
    page: int = 1,
    db: Session = Depends(get_db_session),
):
    PAGE_SIZE = 20
    repo = LeadsRepository(db)

    query = repo.base_query(state=state)

    total = query.count()
    leads = (
        query
        .order_by(Lead.created_at.desc())
        .offset((page - 1) * PAGE_SIZE)
        .limit(PAGE_SIZE)
        .all()
    )

    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE

    return templates.TemplateResponse(
        "leads.html",
        {
            "request": request,
            "leads": leads,
            "score_class": score_class,
            "state": state,
            "page": page,
            "total_pages": total_pages,
        },
    )


@router.get("/{lead_id}", response_class=HTMLResponse)
def lead_detail(lead_id: int, request: Request, db: Session = Depends(get_db_session)):
    lead = (
        db.query(Lead)
        .options(joinedload(Lead.visited_link))
        .filter(Lead.id == lead_id)
        .first()
    )
    return templates.TemplateResponse("partials/lead_detail.html", {"request": request, "lead": lead})


@router.post("/{lead_id}/state", response_class=HTMLResponse)
def update_state(
    lead_id: int,
    request: Request,
    next_state: str = Form(...),
    db: Session = Depends(get_db_session),
):
    lead = LeadsRepository(db).get(lead_id)
    if not lead:
        return HTMLResponse("<div class='alert alert-danger'>Lead not found</div>", status_code=404)

    try:
        current_state = lead.state
        if current_state == "IN_REVIEW" and next_state == "APPROVED":
            subject, body = DraftService.generate_for_lead(lead)
            lead.email_subject = subject
            lead.email_body = body
        lead.state = LeadStateMachine.transition(lead.state, next_state)
        db.commit()
        message = f"State updated to {lead.state}"
        css = "success"
    except ValueError as exc:
        db.rollback()
        message = str(exc)
        css = "danger"

    return HTMLResponse(f"<div class='alert alert-{css}'>{message}</div>")


@router.post("/{lead_id}/edit", response_class=HTMLResponse)
def edit_lead(
    lead_id: int,
    company: str = Form(default=""),
    email: str = Form(default=""),
    role: str = Form(default=""),
    recruiter: str = Form(default=""),
    db: Session = Depends(get_db_session),
):
    lead = LeadsRepository(db).get(lead_id)
    if not lead:
        return HTMLResponse("<div class='alert alert-danger'>Lead not found</div>", status_code=404)

    lead.company = company.strip() or None
    lead.email = email.strip() or None
    lead.role = role.strip() or None
    lead.recruiter = recruiter.strip() or None
    db.commit()
    return HTMLResponse("<div class='alert alert-success'>Lead updated</div>")


@router.post("/{lead_id}/send-mail", response_class=HTMLResponse)
def send_mail(lead_id: int, db: Session = Depends(get_db_session)):
    lead = LeadsRepository(db).get(lead_id)
    if not lead:
        return HTMLResponse("<div class='alert alert-danger'>Lead not found</div>", status_code=404)
    if not lead.email:
        return HTMLResponse("<div class='alert alert-danger'>Lead email missing</div>", status_code=400)

    service = GmailMailService(get_settings().gmail_token_file)
    try:
        service.send_for_lead(lead, lead.email, lead.email_subject or "Opportunity", lead.email_body or "Hello")
        db.commit()
        return HTMLResponse("<div class='alert alert-success'>Mail sent</div>")
    except MailTokenError as exc:
        db.rollback()
        return HTMLResponse(f"<div class='alert alert-danger'>Token error: {exc}</div>", status_code=400)
    except Exception as exc:
        db.commit()
        return HTMLResponse(f"<div class='alert alert-warning'>Mail failed: {exc}</div>")


@router.post("/bulk-send", response_class=HTMLResponse)
def bulk_send(db: Session = Depends(get_db_session)):
    repo = LeadsRepository(db)
    approved = repo.approved()
    service = GmailMailService(get_settings().gmail_token_file)

    sent = 0
    failed = 0
    for lead in approved:
        if not lead.email:
            lead.state = LeadStateMachine.transition(lead.state, "MAIL_FAILED")
            lead.mail_failure_reason = "Missing email"
            failed += 1
            continue
        try:
            service.send_for_lead(lead, lead.email, lead.email_subject or "Opportunity", lead.email_body or "Hello")
            sent += 1
        except MailTokenError as exc:
            db.rollback()
            return HTMLResponse(f"<div class='alert alert-danger'>Token error: {exc}</div>", status_code=400)
        except Exception as exc:
            lead.state = LeadStateMachine.transition(lead.state, "MAIL_FAILED")
            lead.mail_failure_reason = str(exc)
            failed += 1

    db.commit()
    return HTMLResponse(f"<div class='alert alert-info'>Bulk mail done. Sent={sent}, Failed={failed}</div>")


@router.post("/{lead_id}/delete", response_class=HTMLResponse)
def delete_lead(lead_id: int, db: Session = Depends(get_db_session)):
    lead = LeadsRepository(db).get(lead_id)
    if not lead:
        return HTMLResponse("<div class='alert alert-danger'>Lead not found</div>", status_code=404)

    db.delete(lead)
    db.commit()

    return HTMLResponse("")


@router.post("/bulk-delete", response_class=HTMLResponse)
async def bulk_delete(request: Request, db: Session = Depends(get_db_session)):
    form = await request.form()
    ids = form.getlist("lead_ids")

    if not ids:
        return HTMLResponse("<div class='alert alert-warning'>No leads selected</div>")

    for lead_id in ids:
        lead = LeadsRepository(db).get(int(lead_id))
        if lead:
            db.delete(lead)

    db.commit()

    return HTMLResponse(
        "",
        headers={"HX-Redirect": "/leads"}
    )
