import json
import time
from openai import OpenAI, RateLimitError

from app.core.config import get_settings
from app.llm.base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self):
        settings = get_settings()
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY missing")
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def analyze(self, raw_text: str) -> dict:
        settings = get_settings()
        max_retries = settings.llm_max_retries
        base = settings.llm_backoff_base_seconds

        system = (
            "You analyze LinkedIn hiring posts. Output strict JSON only. "
            "Ignore comments/replies/reactions/navigation. "
            "Extract role, experience, seniority, location, company, recruiter, recruiter_profile_link, email, score. "
            "Score is 0-100 where relevance to active hiring and actionable outreach is high."
        )
        user = f"Post text:\n{raw_text}"
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    temperature=0,
                    messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                    response_format={"type": "json_object"},
                )
                content = response.choices[0].message.content or "{}"
                try:
                    return json.loads(content)
                except Exception as exc:
                    raise ValueError(f"Invalid LLM JSON response raw={content}") from exc
            except RateLimitError:
                time.sleep(base * (2 ** attempt))
                continue
            except Exception as exc:
                if "429" in str(exc):
                    time.sleep(base * (2 ** attempt))
                    continue
                raise
        raise RuntimeError("LLM rate limit exceeded after retries")
