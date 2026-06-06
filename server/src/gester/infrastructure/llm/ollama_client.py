import requests


class OllamaClient:
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen2.5:7b-instruct",
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model

    def generate(self, prompt: str) -> str:
        response = requests.post(
            f"{self._base_url}/api/generate",
            json={
                "model": self._model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()
        return data["response"]