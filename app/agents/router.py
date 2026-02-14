from app.config import SYSTEM_PRIMARY_AGENT, SYSTEM_FALLBACK_AGENT, TASK_CONFIG
from .openai_agent import OpenAIAgent
from .gemini_agent import GeminiAgent
from app.tasks.task_definitions import TASK_DEFINITIONS

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

        if task_name not in TASK_DEFINITIONS:
            raise ValueError(f"Unknown task: {task_name}")

        schema = TASK_DEFINITIONS[task_name]["output_schema"]

        enriched_payload = {
            "task": task_name,
            "input": payload,
            "expected_output_schema": schema
        }

        primary, fallback = self.resolve_agents(task_name)

        try:
            result = self.agents[primary].execute(task_name, enriched_payload)
            return result, primary

        except Exception as e:
            print(f"[Router] Primary {primary} failed: {e}")

            if fallback and fallback in self.agents:
                result = self.agents[fallback].execute(task_name, enriched_payload)
                return result, fallback

            raise RuntimeError("Both primary and fallback failed")

