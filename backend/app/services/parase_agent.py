from openai import OpenAI
import json
from typing import Dict


class ParseAgent:
    def __init__(
        self,
        open_router_api_key: str,
        system_prompt: str,
        model: str,
    ):
        self.client = OpenAI(
            api_key=open_router_api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://github.com",
                "X-Title": "Parse Agent",
            },
        )

        self.model = model
        self.system_prompt = system_prompt

    def parse_message(self, message: str, temperature: float = 0.1) -> Dict:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": message},
                ],
                temperature=temperature,
                response_format={"type": "json_object"},
            )

            parased_reply = response.choices[0].message.content

            parased_reply = json.loads(parased_reply)

            return parased_reply
        except Exception as e:
            print(f"error parasing message: {e}")
            return {"error": str(e), "orginal_message": message}

    def update_system_prompt(self, new_prompt: str) -> None:
        self.system_prompt = new_prompt

    def change_model(self, new_model: str) -> None:
        self.model = new_model
