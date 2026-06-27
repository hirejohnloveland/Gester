from fastapi import APIRouter

from gester.application.ingestion.rss_ingestion_service import RssIngestionService
from gester.application.ingestion.source_item_chunking_service import SourceItemChunkingService
from gester.application.ingestion.chunk_embedding_service import ChunkEmbeddingService

router = APIRouter(tags=["ingestion"])


@router.post("/ingest/rss")
def ingest_rss():
    service = RssIngestionService()
    saved_count = service.ingest("https://www.xda-developers.com/feed/")

    return {"saved_count": saved_count}


@router.post("/process/chunks")
def process_chunks():
    service = SourceItemChunkingService()
    chunked_item_count = service.chunk_missing_source_items()

    return {"chunked_item_count": chunked_item_count}


@router.post("/process/chunks/reset")
def reset_chunks():
    service = SourceItemChunkingService()
    deleted_chunk_count = service.reset_chunks()

    return {"deleted_chunk_count": deleted_chunk_count}


@router.post("/process/embeddings")
def process_embeddings(rebuild: bool = False):
    service = ChunkEmbeddingService()

    embedded_count = service.embed_chunks(rebuild=rebuild)

    return {
        "embedded_count": embedded_count,
        "rebuild": rebuild,
    }
