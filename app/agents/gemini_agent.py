import os
import json
from google import genai
from .base_agent import BaseAgent

class GeminiAgent(BaseAgent):

    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = "gemini-1.5-flash"

    def execute(self, task_name: str, payload: dict) -> dict:

        prompt = f"""
        You are an AI agent performing task: {task_name}.
        Return strictly valid JSON only.
        Do not include explanations.

        Input:
        {payload["input"]}

        Expected JSON schema:
        {payload["expected_output_schema"]}
        """

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        text = response.text.strip()

        try:
            return json.loads(text)
        except:
            raise Exception("Gemini returned invalid JSON")
