from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SourceItemResponse(BaseModel):
    id: int
    source_type: str
    title: str
    url: str | None = None
    raw_content: str | None = None
    published_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)