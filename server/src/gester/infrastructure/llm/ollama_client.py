import requests


class OllamaClient:
    def __init__(
        self,
        base_url: str,
        model: str,
        temperature: float,
        timeout: int,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._temperature = temperature
        self._timeout = timeout

    def generate(self, prompt: str) -> str:
        response = requests.post(
            f"{self._base_url}/api/generate",
            json={
                "model": self._model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self._temperature,
                },
            },
            timeout=self._timeout,
        )

        response.raise_for_status()

        data = response.json()
        return data["response"]
