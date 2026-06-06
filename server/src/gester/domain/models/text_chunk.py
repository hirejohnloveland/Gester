from pydantic import BaseModel


class TextChunk(BaseModel):
    char_start: int
    char_end: int
    chunk_text: str