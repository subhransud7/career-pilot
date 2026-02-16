from types import SimpleNamespace
import pytest

from app.core.errors import MailTokenError
from app.services.mail_service import GmailMailService


class DummyLead:
    def __init__(self, state="APPROVED"):
        self.state = state
        self.mail_failure_reason = None


class _MsgSender:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail

    def send(self, userId, body):
        if self.should_fail:
            raise RuntimeError("gmail send failed")
        return SimpleNamespace(execute=lambda: {"id": "ok"})


class _Users:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail

    def messages(self):
        return _MsgSender(self.should_fail)


class _Service:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail

    def users(self):
        return _Users(self.should_fail)


def test_mail_success(monkeypatch):
    monkeypatch.setattr(
        "app.services.mail_service.Credentials.from_authorized_user_file",
        lambda _: SimpleNamespace(valid=True, expired=False, refresh_token=None),
    )
    monkeypatch.setattr("app.services.mail_service.build", lambda *args, **kwargs: _Service(False))

    lead = DummyLead("APPROVED")
    GmailMailService("token.json").send_for_lead(lead, "a@b.com", "sub", "body")
    assert lead.state == "MAILED"
    assert lead.mail_failure_reason is None


def test_mail_failure_transitions_mail_failed(monkeypatch):
    monkeypatch.setattr(
        "app.services.mail_service.Credentials.from_authorized_user_file",
        lambda _: SimpleNamespace(valid=True, expired=False, refresh_token=None),
    )
    monkeypatch.setattr("app.services.mail_service.build", lambda *args, **kwargs: _Service(True))

    lead = DummyLead("APPROVED")
    with pytest.raises(RuntimeError):
        GmailMailService("token.json").send_for_lead(lead, "a@b.com", "sub", "body")
    assert lead.state == "MAIL_FAILED"
    assert "gmail send failed" in lead.mail_failure_reason


def test_invalid_token_raises_controlled(monkeypatch):
    monkeypatch.setattr(
        "app.services.mail_service.Credentials.from_authorized_user_file",
        lambda _: (_ for _ in ()).throw(ValueError("bad token")),
    )
    lead = DummyLead("APPROVED")
    with pytest.raises(MailTokenError):
        GmailMailService("token.json").send_for_lead(lead, "a@b.com", "sub", "body")
    assert lead.state == "APPROVED"
