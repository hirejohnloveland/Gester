from typing import Annotated

from fastapi import APIRouter, Depends

from gester.api.dependencies import (
    SettingsDep,
    get_chunk_embedding_service,
    get_rss_ingestion_service,
    get_source_item_chunking_service,
)
from gester.application.ingestion.chunk_embedding_service import ChunkEmbeddingService
from gester.application.ingestion.rss_ingestion_service import RssIngestionService
from gester.application.ingestion.source_item_chunking_service import SourceItemChunkingService

router = APIRouter(tags=["ingestion"])


@router.post("/ingest/rss")
def ingest_rss(
    settings: SettingsDep,
    service: Annotated[RssIngestionService, Depends(get_rss_ingestion_service)],
):
    feed_results = []
    total_saved = 0

    for feed in settings.enabled_feeds:
        saved_count = service.ingest(
            feed.url,
            max_age_days=feed.max_age_days,
            max_items_per_feed=feed.max_items_per_feed,
        )
        total_saved += saved_count

        feed_results.append(
            {
                "name": feed.name,
                "url": feed.url,
                "saved_count": saved_count,
            }
        )

    return {
        "total_saved": total_saved,
        "feeds": feed_results,
    }


@router.post("/process/chunks")
def process_chunks(
    service: Annotated[SourceItemChunkingService, Depends(get_source_item_chunking_service)],
):
    chunked_item_count = service.chunk_missing_source_items()

    return {"chunked_item_count": chunked_item_count}


@router.post("/process/chunks/reset")
def reset_chunks(
    service: Annotated[SourceItemChunkingService, Depends(get_source_item_chunking_service)],
):
    deleted_chunk_count = service.reset_chunks()

    return {"deleted_chunk_count": deleted_chunk_count}


@router.post("/process/embeddings")
def process_embeddings(
    service: Annotated[ChunkEmbeddingService, Depends(get_chunk_embedding_service)],
    rebuild: bool = False,
):
    embedded_count = service.embed_chunks(rebuild=rebuild)

    return {
        "embedded_count": embedded_count,
        "rebuild": rebuild,
    }
