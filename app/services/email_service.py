import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


class EmailService:

    def __init__(self, token_file="gmail_token.json"):
        self.creds = Credentials.from_authorized_user_file(token_file)
        self.service = build("gmail", "v1", credentials=self.creds)

    def send_email(self, to_email: str, subject: str, body: str):

        message = MIMEText(body)
        message["to"] = to_email
        message["subject"] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        self.service.users().messages().send(
            userId="me",
            body={"raw": raw}
        ).execute()
