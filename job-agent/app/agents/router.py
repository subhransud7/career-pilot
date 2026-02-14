from app.config import SYSTEM_PRIMARY_AGENT, SYSTEM_FALLBACK_AGENT, TASK_CONFIG
from .openai_agent import OpenAIAgent
from .gemini_agent import GeminiAgent

class AgentRouter:

    def __init__(self):
        self.agents = {
            "openai": OpenAIAgent(),
            "gemini": GeminiAgent()
        }

    def resolve_agents(self, task_name: str):

        task_conf = TASK_CONFIG.get(task_name, {})

        primary = task_conf.get("primary", SYSTEM_PRIMARY_AGENT)
        fallback = task_conf.get("fallback", SYSTEM_FALLBACK_AGENT)

        return primary, fallback

    def run(self, task_name: str, payload: dict):

        primary, fallback = self.resolve_agents(task_name)

        try:
            result = self.agents[primary].execute(task_name, payload)
            return result, primary

        except Exception as e:
            print(f"[Router] Primary {primary} failed: {e}")

            if fallback and fallback in self.agents:
                try:
                    result = self.agents[fallback].execute(task_name, payload)
                    return result, fallback
                except Exception as e2:
                    print(f"[Router] Fallback {fallback} failed: {e2}")
                    raise RuntimeError("Both primary and fallback failed")

            raise RuntimeError("No valid fallback agent")
