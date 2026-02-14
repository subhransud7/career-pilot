from app.schemas.task_models import (
    AnalyzePostModel,
    ScoreJobModel,
    EmailModel,
    LinkedInMessageModel
)

TASK_DEFINITIONS = {

    "analyze_post": {
        "description": "Extract structured job information from LinkedIn post text.",
        "output_schema": {
            "role": "string",
            "experience": "string",
            "seniority": "string",
            "location": "string",
            "company": "string",
            "recruiter": "string",
            "recruiter_profile_link": "string",
            "email": "string",
            "needs_cv": "boolean"
        }
    },

    "score_job": {
        "description": "Score how relevant the job is for the candidate.",
        "output_schema": {
            "score": "integer (0-10)",
            "reason": "string"
        }
    },

    "generate_email": {
        "description": "Generate a professional job application email.",
        "output_schema": {
            "subject": "string",
            "body": "string"
        }
    },

    "generate_linkedin_message": {
        "description": "Generate a concise LinkedIn DM message.",
        "output_schema": {
            "message": "string"
        }
    }
}

TASK_VALIDATORS = {
    "analyze_post": AnalyzePostModel,
    "score_job": ScoreJobModel,
    "generate_email": EmailModel,
    "generate_linkedin_message": LinkedInMessageModel
}

