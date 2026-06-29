from datetime import datetime

from pydantic import BaseModel, ConfigDict

from gester.domain.models.evaluation_corpus import (
    ChunkingStrategySnapshot,
    EmbeddingConfigSnapshot,
    EvaluationCorpus,
    EvaluationCorpusArticleSnapshot,
    EvaluationCorpusStats,
)


class EvaluationCorpusSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str
    created_at: datetime
    chunking_strategy: ChunkingStrategySnapshot
    embedding: EmbeddingConfigSnapshot
    ingestion_earliest_at: datetime | None
    ingestion_latest_at: datetime | None
    embedding_latest_at: datetime | None
    stats: EvaluationCorpusStats

    @classmethod
    def from_corpus(cls, corpus: EvaluationCorpus) -> "EvaluationCorpusSummaryResponse":
        return cls(
            version=corpus.version,
            created_at=corpus.created_at,
            chunking_strategy=corpus.chunking_strategy,
            embedding=corpus.embedding,
            ingestion_earliest_at=corpus.ingestion_earliest_at,
            ingestion_latest_at=corpus.ingestion_latest_at,
            embedding_latest_at=corpus.embedding_latest_at,
            stats=corpus.stats,
        )


class EvaluationCorpusDetailResponse(EvaluationCorpusSummaryResponse):
    article_ids: list[int]
    chunk_ids: list[int]
    articles: list[EvaluationCorpusArticleSnapshot]

    @classmethod
    def from_corpus(cls, corpus: EvaluationCorpus) -> "EvaluationCorpusDetailResponse":
        return cls(
            **EvaluationCorpusSummaryResponse.from_corpus(corpus).model_dump(),
            article_ids=corpus.article_ids,
            chunk_ids=corpus.chunk_ids,
            articles=corpus.articles,
        )
