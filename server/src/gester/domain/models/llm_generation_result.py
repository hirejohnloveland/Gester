from pydantic import BaseModel


class LlmGenerationResult(BaseModel):
    content: str
    thinking: str | None = None
