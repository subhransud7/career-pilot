import pytest
from app.core.state_machine import LeadStateMachine


def test_valid_transitions():
    assert LeadStateMachine.transition("IN_REVIEW", "APPROVED") == "APPROVED"
    assert LeadStateMachine.transition("APPROVED", "MAILED") == "MAILED"
    assert LeadStateMachine.transition("MAILED", "WAITING_RESPONSE") == "WAITING_RESPONSE"


def test_invalid_transition_raises():
    with pytest.raises(ValueError):
        LeadStateMachine.transition("IN_REVIEW", "MAILED")
