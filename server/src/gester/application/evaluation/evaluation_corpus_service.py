import logging
from collections import defaultdict
from datetime import date, datetime, timezone

from gester.configuration.app_settings import AppSettings
from gester.domain.models.evaluation_corpus import (
    ChunkingStrategySnapshot,
    EmbeddingConfigSnapshot,
    EvaluationCorpus,
    EvaluationCorpusArticleSnapshot,
    EvaluationCorpusStats,
)
from gester.infrastructure.storage.eval.eval_corpus_file_store import EvalCorpusFileStore
from gester.infrastructure.storage.sqlite.source_item_chunk_repository import SourceItemChunkRepository
from gester.infrastructure.storage.sqlite.source_item_repository import SourceItemRepository

logger = logging.getLogger(__name__)


class EvaluationCorpusService:
    def __init__(
        self,
        settings: AppSettings,
        source_item_repository: SourceItemRepository,
        chunk_repository: SourceItemChunkRepository,
        corpus_file_store: EvalCorpusFileStore,
    ) -> None:
        self._settings = settings
        self._source_item_repository = source_item_repository
        self._chunk_repository = chunk_repository
        self._corpus_file_store = corpus_file_store

    def create_corpus(self, version: str | None = None) -> EvaluationCorpus:
        resolved_version = version or self._default_version_name()

        if self._corpus_file_store.exists(resolved_version):
            raise ValueError(f"Evaluation corpus already exists: {resolved_version}")

        corpus = self._build_corpus(resolved_version)
        self._corpus_file_store.save(corpus)

        logger.info(
            "Created evaluation corpus %s (%d articles, %d chunks)",
            corpus.version,
            corpus.stats.article_count,
            corpus.stats.chunk_count,
        )

        return corpus

    def list_corpora(self) -> list[EvaluationCorpus]:
        return [self._corpus_file_store.load(version) for version in self._corpus_file_store.list_versions()]

    def get_corpus(self, version: str) -> EvaluationCorpus:
        return self._corpus_file_store.load(version)

    def _build_corpus(self, version: str) -> EvaluationCorpus:
        articles = self._source_item_repository.get_all()
        chunks = self._chunk_repository.get_all()

        chunks_by_article_id: dict[int, list[int]] = defaultdict(list)

        for chunk in chunks:
            if chunk.id is None:
                continue

            chunks_by_article_id[chunk.source_item_id].append(chunk.id)

        for chunk_ids in chunks_by_article_id.values():
            chunk_ids.sort()

        article_snapshots: list[EvaluationCorpusArticleSnapshot] = []

        for article in articles:
            if article.id is None or article.created_at is None:
                continue

            article_snapshots.append(
                EvaluationCorpusArticleSnapshot(
                    id=article.id,
                    source_type=article.source_type,
                    title=article.title,
                    url=article.url,
                    published_at=article.published_at,
                    created_at=article.created_at,
                    chunk_ids=chunks_by_article_id.get(article.id, []),
                )
            )

        article_snapshots.sort(key=lambda article: article.id)
        article_ids = [article.id for article in article_snapshots]
        chunk_ids = sorted(chunk.id for chunk in chunks if chunk.id is not None)

        embedded_chunk_count = sum(1 for chunk in chunks if chunk.embedded_at is not None)
        article_created_at = [article.created_at for article in article_snapshots]
        embedded_at_values = [
            chunk.embedded_at for chunk in chunks if chunk.embedded_at is not None
        ]

        return EvaluationCorpus(
            version=version,
            created_at=datetime.now(timezone.utc),
            chunking_strategy=ChunkingStrategySnapshot(
                method="fixed_size_char",
                chunk_size=self._settings.chunking.chunk_size,
                overlap=self._settings.chunking.overlap,
            ),
            embedding=EmbeddingConfigSnapshot(
                model_name=self._settings.embedding.model_name,
                collection_name=self._settings.vector_store.collection_name,
                vector_size=self._settings.vector_store.vector_size,
                distance=self._settings.vector_store.distance,
            ),
            ingestion_earliest_at=min(article_created_at) if article_created_at else None,
            ingestion_latest_at=max(article_created_at) if article_created_at else None,
            embedding_latest_at=max(embedded_at_values) if embedded_at_values else None,
            stats=EvaluationCorpusStats(
                article_count=len(article_snapshots),
                chunk_count=len(chunk_ids),
                embedded_chunk_count=embedded_chunk_count,
                unembedded_chunk_count=len(chunk_ids) - embedded_chunk_count,
            ),
            article_ids=article_ids,
            chunk_ids=chunk_ids,
            articles=article_snapshots,
        )

    def _default_version_name(self) -> str:
        base_name = f"baseline_{date.today().isoformat().replace('-', '_')}"
        version = base_name
        suffix = 2

        while self._corpus_file_store.exists(version):
            version = f"{base_name}_{suffix}"
            suffix += 1

        return version
