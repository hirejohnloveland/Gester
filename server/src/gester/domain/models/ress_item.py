from dataclasses import dataclass
from datetime import datetime


class RssItem(BaseModel):
    title: str
    link: str
    summary: str | None = None
    published_at: datetime | None = None
    source_type: str = Field(default="rss")