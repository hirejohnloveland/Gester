from fastapi import FastAPI

from gester.api.routers import content_router, ingestion_router, retrieval_router
from gester.infrastructure.storage.sqlite.sqlite_db import initialize_database

app = FastAPI(title="Gester API")

app.include_router(content_router.router)
app.include_router(ingestion_router.router)
app.include_router(retrieval_router.router)


@app.on_event("startup")
def startup() -> None:
    initialize_database()


def main() -> None:
    import uvicorn

    uvicorn.run(
        "gester.app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
