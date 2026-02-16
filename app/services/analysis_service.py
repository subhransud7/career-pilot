import logging

from app.core.config import get_settings
from app.llm.registry import get_provider
from app.schemas.analysis import AnalysisResult

logger = logging.getLogger(__name__)


class AnalysisService:
    def __init__(self):
        settings = get_settings()
        self.provider = get_provider(settings.llm_provider)

    def analyze_post(self, raw_text: str) -> dict:
        try:
            parsed = self.provider.analyze(raw_text)

            # Normalize all scalar fields to string if not None
            normalized = {}

            for key, value in parsed.items():

                # If list → take first element
                if isinstance(value, list):
                    value = value[0] if value else None

                # Convert non-string scalars to string
                if value is not None and not isinstance(value, str):
                    value = str(value)

                normalized[key] = value

            validated = AnalysisResult(**normalized)
            return validated.model_dump()

        except Exception as exc:
            logger.error("Invalid LLM JSON response error=%s", exc)
            raise ValueError("Invalid LLM JSON response") from exc

