from pydantic import BaseModel, ConfigDict


class FeedSourceSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    url: str
    enabled: bool = True
