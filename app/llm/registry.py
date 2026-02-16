from app.llm.base import LLMProvider
from app.llm.gemini_provider import GeminiProvider
from app.llm.openai_provider import OpenAIProvider


def get_provider(name: str) -> LLMProvider:
    mapping = {
        "gemini": GeminiProvider,
        "openai": OpenAIProvider,
    }
    if name not in mapping:
        raise ValueError(f"Unknown LLM provider: {name}")
    return mapping[name]()
