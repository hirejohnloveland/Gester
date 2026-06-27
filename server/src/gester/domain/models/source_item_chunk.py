from datetime import datetime

from pydantic import BaseModel


class SourceItemChunk(BaseModel):
    id: int | None = None
    source_item_id: int
    embedded_at: datetime | None = None
    chunk_index: int
    chunk_text: str
    char_start: int
    char_end: int
    created_at: datetime | None = None
