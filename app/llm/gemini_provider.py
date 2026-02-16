import json
import time
from google import genai

from app.core.config import get_settings
from app.llm.base import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self):
        settings = get_settings()
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY missing")
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_model

    def analyze(self, raw_text: str) -> dict:
        settings = get_settings()
        max_retries = settings.llm_max_retries
        base = settings.llm_backoff_base_seconds

        prompt = (
            "You analyze LinkedIn hiring posts. Return strict JSON only. "
            "Ignore comments/replies/reactions/navigation. "
            "Extract role, experience, seniority, location, company, recruiter, recruiter_profile_link, email, score. "
            "Score is 0-100 where relevance to active hiring and actionable outreach is high.\n\n"
            f"Post text:\n{raw_text}"
        )
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(model=self.model, contents=prompt)
                content = (response.text or "{}")
                content = content.strip()
                if content.startswith("```"):
                    content = content.replace("```json", "").replace("```", "").strip()
                try:
                    parsed = json.loads(content)

                    # Normalize if Gemini returns a list
                    if isinstance(parsed, list):
                        if not parsed:
                            raise ValueError("Empty JSON list returned from Gemini")
                        parsed = parsed[0]

                    if not isinstance(parsed, dict):
                        raise ValueError(f"Gemini returned unexpected JSON type: {type(parsed)}")

                    return parsed
                except Exception as exc:
                    raise ValueError(f"Invalid LLM JSON response raw={content}") from exc
            except Exception as exc:
                if "429" in str(exc):
                    if attempt == max_retries - 1:
                        break
                    time.sleep(base * (2 ** attempt))
                    continue
                raise
        raise RuntimeError("LLM rate limit exceeded after retries")
