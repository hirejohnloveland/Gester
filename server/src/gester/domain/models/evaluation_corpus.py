from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChunkingStrategySnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    method: str
    chunk_size: int
    overlap: int


class EmbeddingConfigSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model_name: str
    collection_name: str
    vector_size: int
    distance: str


class EvaluationCorpusArticleSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    source_type: str
    title: str
    url: str | None = None
    published_at: datetime | None = None
    created_at: datetime
    chunk_ids: list[int] = Field(default_factory=list)


class EvaluationCorpusStats(BaseModel):
    model_config = ConfigDict(extra="forbid")

    article_count: int
    chunk_count: int
    embedded_chunk_count: int
    unembedded_chunk_count: int


class EvaluationCorpus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str
    created_at: datetime
    chunking_strategy: ChunkingStrategySnapshot
    embedding: EmbeddingConfigSnapshot
    ingestion_earliest_at: datetime | None = None
    ingestion_latest_at: datetime | None = None
    embedding_latest_at: datetime | None = None
    stats: EvaluationCorpusStats
    article_ids: list[int]
    chunk_ids: list[int]
    articles: list[EvaluationCorpusArticleSnapshot]
