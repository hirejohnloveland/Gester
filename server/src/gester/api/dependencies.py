from typing import Annotated

from fastapi import Depends, Request
from qdrant_client.models import Distance
from sqlalchemy.orm import sessionmaker

from gester.application.evaluation.evaluation_corpus_service import EvaluationCorpusService
from gester.application.evaluation.golden_question_service import (
    GoldenQuestionService,
    GoldenQuestionValidationResult,
)
from gester.application.evaluation.retrieval_eval_service import RetrievalEvalService
from gester.application.content.source_item_chunk_query_service import SourceItemChunkQueryService
from gester.application.content.source_item_query_service import SourceItemQueryService
from gester.application.ingestion.chunk_embedding_service import ChunkEmbeddingService
from gester.application.ingestion.rss_ingestion_service import RssIngestionService
from gester.application.ingestion.source_item_chunking_service import SourceItemChunkingService
from gester.application.ingestion.text_chunking_service import TextChunkingService
from gester.application.retrieval.answer_service import AnswerService
from gester.application.retrieval.search_service import SearchService
from gester.configuration.app_settings import AppSettings
from gester.infrastructure.embeddings.embedding_service import EmbeddingService
from gester.infrastructure.extraction.article_extractor import ArticleExtractor
from gester.infrastructure.feeds.rss_reader import RssReader
from gester.infrastructure.llm.ollama_client import OllamaClient
from gester.infrastructure.storage.eval.eval_corpus_file_store import EvalCorpusFileStore
from gester.infrastructure.storage.eval.eval_run_file_store import EvalRunFileStore
from gester.infrastructure.storage.eval.golden_question_file_store import GoldenQuestionFileStore
from gester.infrastructure.storage.sqlite.source_item_chunk_repository import SourceItemChunkRepository
from gester.infrastructure.storage.sqlite.source_item_repository import SourceItemRepository
from gester.infrastructure.storage.vector.qdrant_vector_store import QdrantVectorStore

_DISTANCE_BY_NAME = {
    "cosine": Distance.COSINE,
    "dot": Distance.DOT,
    "euclid": Distance.EUCLID,
    "manhattan": Distance.MANHATTAN,
}


def get_settings(request: Request) -> AppSettings:
    return request.app.state.settings


def get_session_factory(request: Request) -> sessionmaker:
    return request.app.state.session_factory


SettingsDep = Annotated[AppSettings, Depends(get_settings)]
SessionFactoryDep = Annotated[sessionmaker, Depends(get_session_factory)]


def get_source_item_repository(
    session_factory: SessionFactoryDep,
) -> SourceItemRepository:
    return SourceItemRepository(session_factory)


def get_source_item_chunk_repository(
    session_factory: SessionFactoryDep,
) -> SourceItemChunkRepository:
    return SourceItemChunkRepository(session_factory)


def get_rss_reader() -> RssReader:
    return RssReader()


def get_article_extractor() -> ArticleExtractor:
    return ArticleExtractor()


def get_text_chunking_service(settings: SettingsDep) -> TextChunkingService:
    return TextChunkingService(
        chunk_size=settings.chunking.chunk_size,
        overlap=settings.chunking.overlap,
    )


def get_embedding_service(settings: SettingsDep) -> EmbeddingService:
    return EmbeddingService(settings.embedding.model_name)


def get_vector_store(settings: SettingsDep) -> QdrantVectorStore:
    distance_name = settings.vector_store.distance.lower()
    distance = _DISTANCE_BY_NAME.get(distance_name)

    if distance is None:
        raise ValueError(f"Unsupported vector store distance: {settings.vector_store.distance}")

    return QdrantVectorStore(
        path=settings.qdrant_path,
        collection_name=settings.vector_store.collection_name,
        vector_size=settings.vector_store.vector_size,
        distance=distance,
    )


def get_llm_client(settings: SettingsDep) -> OllamaClient:
    return OllamaClient(
        base_url=settings.llm.base_url,
        model=settings.llm.model,
        temperature=settings.llm.temperature,
        timeout=settings.llm.timeout,
        think=settings.llm.think,
        num_ctx=settings.llm.num_ctx,
    )


SourceItemRepositoryDep = Annotated[SourceItemRepository, Depends(get_source_item_repository)]
SourceItemChunkRepositoryDep = Annotated[
    SourceItemChunkRepository, Depends(get_source_item_chunk_repository)
]
TextChunkingServiceDep = Annotated[TextChunkingService, Depends(get_text_chunking_service)]
EmbeddingServiceDep = Annotated[EmbeddingService, Depends(get_embedding_service)]
VectorStoreDep = Annotated[QdrantVectorStore, Depends(get_vector_store)]
LlmClientDep = Annotated[OllamaClient, Depends(get_llm_client)]


def get_rss_ingestion_service(
    settings: SettingsDep,
    rss_reader: Annotated[RssReader, Depends(get_rss_reader)],
    article_extractor: Annotated[ArticleExtractor, Depends(get_article_extractor)],
    repository: SourceItemRepositoryDep,
    chunking_service: TextChunkingServiceDep,
    chunk_repository: SourceItemChunkRepositoryDep,
) -> RssIngestionService:
    return RssIngestionService(
        rss_reader=rss_reader,
        article_extractor=article_extractor,
        repository=repository,
        chunking_service=chunking_service,
        chunk_repository=chunk_repository,
        max_age_days=settings.ingestion.max_age_days,
        max_items_per_feed=settings.ingestion.max_items_per_feed,
    )


def get_source_item_chunking_service(
    source_item_repository: SourceItemRepositoryDep,
    chunk_repository: SourceItemChunkRepositoryDep,
    chunking_service: TextChunkingServiceDep,
    vector_store: VectorStoreDep,
) -> SourceItemChunkingService:
    return SourceItemChunkingService(
        source_item_repository=source_item_repository,
        chunk_repository=chunk_repository,
        chunking_service=chunking_service,
        vector_store=vector_store,
    )


def get_chunk_embedding_service(
    chunk_repository: SourceItemChunkRepositoryDep,
    source_item_repository: SourceItemRepositoryDep,
    embedding_service: EmbeddingServiceDep,
    vector_store: VectorStoreDep,
) -> ChunkEmbeddingService:
    return ChunkEmbeddingService(
        chunk_repository=chunk_repository,
        source_item_repository=source_item_repository,
        embedding_service=embedding_service,
        vector_store=vector_store,
    )


def get_search_service(
    embedding_service: EmbeddingServiceDep,
    vector_store: VectorStoreDep,
    chunk_repository: SourceItemChunkRepositoryDep,
    source_item_repository: SourceItemRepositoryDep,
) -> SearchService:
    return SearchService(
        embedding_service=embedding_service,
        vector_store=vector_store,
        chunk_repository=chunk_repository,
        source_item_repository=source_item_repository,
    )


def get_answer_service(
    search_service: Annotated[SearchService, Depends(get_search_service)],
    llm_client: LlmClientDep,
) -> AnswerService:
    return AnswerService(
        search_service=search_service,
        llm_client=llm_client,
    )


def get_source_item_query_service(
    repository: SourceItemRepositoryDep,
) -> SourceItemQueryService:
    return SourceItemQueryService(repository)


def get_source_item_chunk_query_service(
    repository: SourceItemChunkRepositoryDep,
) -> SourceItemChunkQueryService:
    return SourceItemChunkQueryService(repository)


def get_eval_corpus_file_store(settings: SettingsDep) -> EvalCorpusFileStore:
    return EvalCorpusFileStore(settings.eval_corpora_dir)


def get_evaluation_corpus_service(
    settings: SettingsDep,
    source_item_repository: SourceItemRepositoryDep,
    chunk_repository: SourceItemChunkRepositoryDep,
    corpus_file_store: Annotated[EvalCorpusFileStore, Depends(get_eval_corpus_file_store)],
) -> EvaluationCorpusService:
    return EvaluationCorpusService(
        settings=settings,
        source_item_repository=source_item_repository,
        chunk_repository=chunk_repository,
        corpus_file_store=corpus_file_store,
    )


def get_golden_question_file_store(settings: SettingsDep) -> GoldenQuestionFileStore:
    return GoldenQuestionFileStore(settings.golden_questions_path)


def get_golden_question_service(
    question_file_store: Annotated[GoldenQuestionFileStore, Depends(get_golden_question_file_store)],
    corpus_service: Annotated[EvaluationCorpusService, Depends(get_evaluation_corpus_service)],
) -> GoldenQuestionService:
    return GoldenQuestionService(
        question_file_store=question_file_store,
        corpus_service=corpus_service,
    )


def get_eval_run_file_store(settings: SettingsDep) -> EvalRunFileStore:
    return EvalRunFileStore(settings.eval_runs_dir)


def get_retrieval_eval_service(
    settings: SettingsDep,
    search_service: Annotated[SearchService, Depends(get_search_service)],
    golden_question_service: Annotated[GoldenQuestionService, Depends(get_golden_question_service)],
    corpus_service: Annotated[EvaluationCorpusService, Depends(get_evaluation_corpus_service)],
    run_file_store: Annotated[EvalRunFileStore, Depends(get_eval_run_file_store)],
) -> RetrievalEvalService:
    return RetrievalEvalService(
        settings=settings,
        search_service=search_service,
        golden_question_service=golden_question_service,
        corpus_service=corpus_service,
        run_file_store=run_file_store,
    )
