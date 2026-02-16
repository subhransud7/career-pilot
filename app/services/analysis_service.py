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
            validated = AnalysisResult(**parsed)
            return validated.model_dump()
        except Exception as exc:
            logger.error("Invalid LLM JSON response error=%s", exc)
            raise ValueError("Invalid LLM JSON response") from exc
