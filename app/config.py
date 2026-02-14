import os
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PRIMARY_AGENT = os.getenv("SYSTEM_PRIMARY_AGENT", "openai")
SYSTEM_FALLBACK_AGENT = os.getenv("SYSTEM_FALLBACK_AGENT", "gemini")

TASK_CONFIG = {
    # Example override
    # "analyze_post": {"primary": "openai", "fallback": "gemini"},
}
