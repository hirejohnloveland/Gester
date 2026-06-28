from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gester.configuration.feed_source_settings import FeedSourceSettings


class ChunkingSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chunk_size: int = Field(gt=0)
    overlap: int = Field(ge=0)


class EmbeddingSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model_name: str


class VectorStoreSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    collection_name: str
    vector_size: int = Field(gt=0)
    distance: str


class LlmSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    base_url: str
    model: str
    temperature: float = Field(ge=0)
    timeout: int = Field(gt=0)
    think: bool = False
    num_ctx: int = Field(default=16384, gt=0)


class RetrievalSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    limit: int = Field(gt=0)
    min_score: float = Field(ge=0)
    dedupe_by_article: bool


class IngestionSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    max_age_days: int = Field(gt=0)
    max_items_per_feed: int = Field(gt=0)


class LoggingSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    level: str
    retention_days: int = Field(gt=0)
    filename: str
    console: bool


class AppSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_root: Path
    data_dir: Path
    feeds: list[FeedSourceSettings]
    ingestion: IngestionSettings
    chunking: ChunkingSettings
    embedding: EmbeddingSettings
    vector_store: VectorStoreSettings
    llm: LlmSettings
    retrieval: RetrievalSettings
    logging: LoggingSettings

    @property
    def database_path(self) -> Path:
        return self.data_dir / "gester.db"

    @property
    def qdrant_path(self) -> Path:
        return self.data_dir / "qdrant"

    @property
    def log_dir(self) -> Path:
        return self.data_dir / "logs"

    @property
    def enabled_feeds(self) -> list[FeedSourceSettings]:
        return [feed for feed in self.feeds if feed.enabled]
