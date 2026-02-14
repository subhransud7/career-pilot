import os
import json
from openai import OpenAI
from .base_agent import BaseAgent

class OpenAIAgent(BaseAgent):

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"

    def execute(self, task_name: str, payload: dict) -> dict:

        system_prompt = f"You are responsible for task: {task_name}. Return JSON only."
        user_prompt = json.dumps(payload)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0
        )

        content = response.choices[0].message.content

        try:
            return json.loads(content)
        except:
            raise Exception("OpenAI returned invalid JSON")
