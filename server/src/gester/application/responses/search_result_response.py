from pydantic import BaseModel


class SearchResultResponse(BaseModel):
    score: float
    chunk_id: int
    source_item_id: int
    title: str
    url: str | None = None
    chunk_text: str