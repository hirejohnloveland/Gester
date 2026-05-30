from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from gester.infrastructure.storage.sqlite.sqlite_db import Base


class SourceItemEntity(Base):
    __tablename__ = "source_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    source_type: Mapped[str] = mapped_column(String(50), nullable=False)

    title: Mapped[str] = mapped_column(String(500), nullable=False)

    url: Mapped[str | None] = mapped_column(String(2000), nullable=True, unique=True)

    raw_content: Mapped[str | None] = mapped_column(Text, nullable=True)

    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
