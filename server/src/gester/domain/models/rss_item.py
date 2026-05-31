from datetime import datetime
from pydantic import BaseModel, Field


class RssItem(BaseModel):
    title: str
    link: str
    summary: str | None = None
    published_at: datetime | None = None
    source_type: str = Field(default="rss")