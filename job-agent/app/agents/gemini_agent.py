import os
import json
import google.generativeai as genai
from .base_agent import BaseAgent

class GeminiAgent(BaseAgent):

    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def execute(self, task_name: str, payload: dict) -> dict:

        prompt = f"""
        You are responsible for task: {task_name}.
        Return JSON only.

        Input:
        {json.dumps(payload)}
        """

        response = self.model.generate_content(prompt)

        try:
            return json.loads(response.text)
        except:
            raise Exception("Gemini returned invalid JSON")
