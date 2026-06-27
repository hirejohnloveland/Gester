from pydantic import BaseModel


class AnswerSourceResponse(BaseModel):
    source_number: int
    source_item_id: int
    chunk_id: int
    title: str
    url: str | None = None
    score: float