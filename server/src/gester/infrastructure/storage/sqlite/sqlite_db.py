from pathlib import Path

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


def create_db_engine(database_path: Path) -> Engine:
    database_path.parent.mkdir(parents=True, exist_ok=True)

    return create_engine(
        f"sqlite:///{database_path}",
        echo=False,
    )


def create_session_factory(engine: Engine) -> sessionmaker:
    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )


def initialize_database(engine: Engine) -> None:
    from gester.infrastructure.storage.sqlite.entities.source_item_chunk_entity import (
        SourceItemChunkEntity,
    )
    from gester.infrastructure.storage.sqlite.entities.source_item_entity import SourceItemEntity

    _ = (SourceItemEntity, SourceItemChunkEntity)

    Base.metadata.create_all(bind=engine)
