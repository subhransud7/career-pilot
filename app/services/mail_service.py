import base64
import os
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from app.core.errors import MailTokenError
from app.core.state_machine import LeadStateMachine

RESUME_PATH = "resume.pdf"
YOUR_EMAIL = "mailsubhransudalai@gmail.com"


class GmailMailService:
    def __init__(self, token_file: str):
        self.token_file = token_file

    def _load_credentials(self):
        try:
            creds = Credentials.from_authorized_user_file(self.token_file)
        except Exception as exc:
            raise MailTokenError(f"Invalid Gmail token file: {exc}") from exc

        if not creds.valid:
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                raise MailTokenError("Gmail token invalid or expired without refresh token")
        return creds

    def send_for_lead(self, lead, to_email: str, subject: str, body: str) -> None:
        creds = self._load_credentials()
        service = build("gmail", "v1", credentials=creds)

        try:
            message = EmailMessage()
            message["To"] = to_email
            message["From"] = YOUR_EMAIL
            message["Subject"] = subject
            message.set_content(body)

            if os.path.exists(RESUME_PATH):
                with open(RESUME_PATH, "rb") as f:
                    message.add_attachment(
                        f.read(),
                        maintype="application",
                        subtype="pdf",
                        filename="Subhransu_Sekhar_Dalai_Resume.pdf"
                    )

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            service.users().messages().send(userId="me", body={"raw": raw}).execute()
            lead.state = LeadStateMachine.transition(lead.state, "MAILED")
            lead.mail_failure_reason = None
        except MailTokenError:
            raise
        except Exception as exc:
            lead.state = LeadStateMachine.transition(lead.state, "MAIL_FAILED")
            lead.mail_failure_reason = str(exc)
            raise
