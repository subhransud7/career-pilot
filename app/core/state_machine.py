class LeadStateMachine:
    ALLOWED = {
        "IN_REVIEW": {"APPROVED", "REJECTED", "ARCHIVED"},
        "APPROVED": {"MAILED", "MAIL_FAILED", "ARCHIVED"},
        "MAIL_FAILED": {"APPROVED"},
        "MAILED": {"WAITING_RESPONSE", "ARCHIVED"},
        "WAITING_RESPONSE": {"RESPONDED", "ARCHIVED"},
    }

    @classmethod
    def transition(cls, current_state: str, next_state: str) -> str:
        if current_state == next_state:
            return current_state
        allowed = cls.ALLOWED.get(current_state, set())
        if next_state not in allowed:
            raise ValueError(f"Invalid transition: {current_state} -> {next_state}")
        return next_state
