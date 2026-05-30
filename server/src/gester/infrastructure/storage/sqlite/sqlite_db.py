from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


PROJECT_ROOT = Path(__file__).resolve().parents[6]
DATABASE_PATH = PROJECT_ROOT / "data" / "gester.db"

engine = create_engine(
    f"sqlite:///{DATABASE_PATH}",
    echo=False,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def initialize_database() -> None:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    from gester.infrastructure.storage.sqlite.entities.source_item_entity import SourceItemEntity

    Base.metadata.create_all(bind=engine)
