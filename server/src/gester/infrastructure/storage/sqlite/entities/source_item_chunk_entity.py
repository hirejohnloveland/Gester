from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from gester.infrastructure.storage.sqlite.sqlite_db import Base


class SourceItemChunkEntity(Base):
    __tablename__ = "source_item_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    source_item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("source_items.id"),
        nullable=False,
        index=True,
    )

    embedded_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
)

    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)

    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)

    char_start: Mapped[int] = mapped_column(Integer, nullable=False)

    char_end: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )