import os
import requests


class ClienteGroq:
    def __init__(self):
        self._base_url = "https://api.groq.com/openai/v1"
        self._headers = {
            "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
            "Content-Type": "application/json",
        }

    def prompt(self, msg: str) -> str:
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": msg}],
        }

        response = requests.post(
            self._base_url + "/chat/completions",
            headers=self._headers,
            json=payload,
        )

        if response.status_code != 200:
            raise Exception(f"Erro: {response.status_code}")

        return response.json()["choices"][0]["message"]["content"]
