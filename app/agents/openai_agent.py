import os
import json
from openai import OpenAI
from .base_agent import BaseAgent

class OpenAIAgent(BaseAgent):

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"

    def execute(self, task_name: str, payload: dict) -> dict:

        system_prompt = f"""
        You are an AI agent performing task: {task_name}.
        You MUST return strictly valid JSON.
        Do not include explanations.
        Do not include markdown.
        """

        user_prompt = f"""
        Input:
        {payload["input"]}

        Expected JSON schema:
        {payload["expected_output_schema"]}
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        try:
            return json.loads(content)
        except:
            raise Exception("OpenAI returned invalid JSON")

