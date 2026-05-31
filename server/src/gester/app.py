from fastapi import FastAPI

from gester.application.ingestion.rss_ingestion_service import RssIngestionService
from gester.application.responses.source_item_response import SourceItemResponse
from gester.infrastructure.storage.sqlite.sqlite_db import initialize_database
from gester.infrastructure.storage.sqlite.source_item_repository import SourceItemRepository

app = FastAPI(title="Gester API")


@app.on_event("startup")
def startup() -> None:
    initialize_database()


@app.get("/items", response_model=list[SourceItemResponse])
def get_items():
    repository = SourceItemRepository()
    return repository.get_all()


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