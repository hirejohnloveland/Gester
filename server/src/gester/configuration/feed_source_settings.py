from pydantic import BaseModel, ConfigDict, Field


class FeedSourceSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    url: str
    enabled: bool = True
    max_age_days: int | None = Field(default=None, gt=0)
    max_items_per_feed: int | None = Field(default=None, gt=0)
