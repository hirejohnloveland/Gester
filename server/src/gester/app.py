import logging

from fastapi import FastAPI

from gester.api.routers import content_router, evaluation_router, ingestion_router, retrieval_router
from gester.configuration.settings_loader import load_settings
from gester.infrastructure.logging.logging_configurator import configure_logging
from gester.infrastructure.storage.sqlite.sqlite_db import (
    create_db_engine,
    create_session_factory,
    initialize_database,
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Gester API")

app.include_router(content_router.router)
app.include_router(ingestion_router.router)
app.include_router(retrieval_router.router)
app.include_router(evaluation_router.router)


@app.on_event("startup")
def startup() -> None:
    settings = load_settings()

    configure_logging(
        log_dir=settings.log_dir,
        level=settings.logging.level,
        retention_days=settings.logging.retention_days,
        filename=settings.logging.filename,
        console=settings.logging.console,
    )

    logger.info("Gester API starting up; data directory %s", settings.data_dir)

    engine = create_db_engine(settings.database_path)

    initialize_database(engine)

    app.state.settings = settings
    app.state.session_factory = create_session_factory(engine)


def main() -> None:
    import uvicorn

    uvicorn.run(
        "gester.app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
