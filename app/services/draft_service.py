from app.models import Lead

FIXED_EXPERIENCE_LINE = (
    "I have 5+ years of experience working on Java and Spring Boot based backend systems, "
    "primarily in microservices and production environments."
)


class DraftService:

    @staticmethod
    def generate_for_lead(lead: Lead) -> tuple[str, str]:

        company = lead.company or ""
        role = lead.role or ""
        recruiter_name = lead.recruiter or ""
        first_name = recruiter_name.split()[0] if recruiter_name else ""

        subject = f"Application for {role} position at {company}"

        greeting = f"Hi {first_name}," if first_name else "Hello,"

        body = f"""{greeting}

I came across your post regarding the {role} opening at {company} and would like to apply.

{FIXED_EXPERIENCE_LINE}

I’ve attached my updated resume for your review. Please let me know if my profile aligns with the requirement, and I’d be happy to discuss further.

Thanks and regards,
Subhransu Sekhar Dalai
"""

        return subject, body
