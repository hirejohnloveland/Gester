from pydantic import BaseModel


class AnswerTimingResponse(BaseModel):
    search_ms: float
    generation_ms: float
    total_ms: float
