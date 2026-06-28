import logging

import requests

from gester.domain.models.llm_generation_result import LlmGenerationResult

logger = logging.getLogger(__name__)

_THINKING_UNSUPPORTED_MARKER = "does not support thinking"


class OllamaClient:
    def __init__(
        self,
        base_url: str,
        model: str,
        temperature: float,
        timeout: int,
        think: bool = False,
        num_ctx: int = 16384,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._temperature = temperature
        self._timeout = timeout
        self._think = think
        self._num_ctx = num_ctx

    def generate(self, prompt: str, think: bool | None = None) -> LlmGenerationResult:
        should_think = think if think is not None else self._think

        response = self._post_chat(prompt, should_think)

        if (
            should_think
            and response.status_code == 400
            and _THINKING_UNSUPPORTED_MARKER in response.text
        ):
            logger.warning(
                "Model %s does not support thinking; retrying without it",
                self._model,
            )
            response = self._post_chat(prompt, False)

        response.raise_for_status()

        message = response.json()["message"]

        return LlmGenerationResult(
            content=message["content"],
            thinking=message.get("thinking"),
        )

    def _post_chat(self, prompt: str, think: bool) -> requests.Response:
        return requests.post(
            f"{self._base_url}/api/chat",
            json={
                "model": self._model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "think": think,
                "options": {
                    "temperature": self._temperature,
                    "num_ctx": self._num_ctx,
                },
            },
            timeout=self._timeout,
        )
