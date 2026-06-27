from fastapi import FastAPI

from gester.application.ingestion.rss_ingestion_service import RssIngestionService
from gester.application.responses.source_item_response import SourceItemResponse
from gester.infrastructure.storage.sqlite.sqlite_db import initialize_database
from gester.infrastructure.storage.sqlite.source_item_repository import SourceItemRepository
from gester.application.ingestion.source_item_chunking_service import SourceItemChunkingService
from gester.infrastructure.storage.sqlite.source_item_chunk_repository import SourceItemChunkRepository
from gester.application.ingestion.chunk_embedding_service import ChunkEmbeddingService
from gester.application.retrieval.search_service import SearchService
from gester.infrastructure.llm.ollama_client import OllamaClient
from gester.application.retrieval.answer_service import AnswerService
from gester.application.responses.answer_response import AnswerResponse

app = FastAPI(title="Gester API")


@app.on_event("startup")
def startup() -> None:
    initialize_database()


@app.get("/items", response_model=list[SourceItemResponse])
def get_items():
    repository = SourceItemRepository()
    items = repository.get_all()

    return [SourceItemResponse.model_validate(item) for item in items]


@app.post("/ingest/rss")
def ingest_rss():
    service = RssIngestionService()
    saved_count = service.ingest("https://www.xda-developers.com/feed/")

    return {"saved_count": saved_count}


def main() -> None:
    import uvicorn

    uvicorn.run(
        "gester.app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )

@app.post("/process/chunks")
def process_chunks():
    service = SourceItemChunkingService()
    chunked_item_count = service.chunk_missing_source_items()

    return {"chunked_item_count": chunked_item_count}

@app.get("/items/{item_id}/chunks")
def get_chunks(item_id: int):
    repository = SourceItemChunkRepository()

    return repository.get_by_source_item_id(item_id)

@app.post("/process/embeddings")
def process_embeddings(rebuild: bool = False):
    service = ChunkEmbeddingService()

    embedded_count = service.embed_chunks(rebuild=rebuild)

    return {
        "embedded_count": embedded_count,
        "rebuild": rebuild,
    }

@app.get("/search")
def search(
    query: str,
    limit: int = 5,
    min_score: float = 0.6,
    dedupe_by_article: bool = True,
):
    service = SearchService()

    results = service.search(query, limit, min_score, dedupe_by_article)

    return results

@app.get("/ask", response_model=AnswerResponse)
def ask(
    question: str,
    limit: int = 5,
    min_score: float = 0.6,
):
    service = AnswerService()

    return service.answer(question, limit, min_score)
