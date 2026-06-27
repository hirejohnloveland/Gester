from datetime import datetime

from pydantic import BaseModel


class SourceItem(BaseModel):
    id: int | None = None
    source_type: str
    title: str
    url: str | None = None
    raw_content: str | None = None
    published_at: datetime | None = None
    created_at: datetime | None = None
