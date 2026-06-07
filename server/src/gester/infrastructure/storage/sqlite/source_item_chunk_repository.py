from datetime import datetime, timezone

from sqlalchemy import select, update

from gester.infrastructure.storage.sqlite.entities.source_item_chunk_entity import (
    SourceItemChunkEntity,
)
from gester.infrastructure.storage.sqlite.sqlite_db import SessionLocal


class SourceItemChunkRepository:
    def add(self, chunk: SourceItemChunkEntity) -> SourceItemChunkEntity:
        with SessionLocal() as session:
            session.add(chunk)
            session.commit()
            session.refresh(chunk)

            return chunk

    def get_by_source_item_id(
        self,
        source_item_id: int,
    ) -> list[SourceItemChunkEntity]:
        with SessionLocal() as session:
            statement = (
                select(SourceItemChunkEntity)
                .where(SourceItemChunkEntity.source_item_id == source_item_id)
                .order_by(SourceItemChunkEntity.chunk_index)
            )

            return list(session.scalars(statement).all())

    def exists_for_source_item_id(self, source_item_id: int) -> bool:
        with SessionLocal() as session:
            statement = select(SourceItemChunkEntity.id).where(
                SourceItemChunkEntity.source_item_id == source_item_id
            )

            return session.scalars(statement).first() is not None

    def get_unembedded_chunks(self) -> list[SourceItemChunkEntity]:
        with SessionLocal() as session:
            statement = (
                select(SourceItemChunkEntity)
                .where(SourceItemChunkEntity.embedded_at.is_(None))
                .order_by(SourceItemChunkEntity.id)
            )

            return list(session.scalars(statement).all())

    def mark_embedded(self, chunk_id: int) -> None:
        with SessionLocal() as session:
            statement = (
                update(SourceItemChunkEntity)
                .where(SourceItemChunkEntity.id == chunk_id)
                .values(embedded_at=datetime.now(timezone.utc))
            )

            session.execute(statement)
            session.commit()
    
    def get_by_id(self, chunk_id: int) -> SourceItemChunkEntity | None:
            with SessionLocal() as session:
                return session.get(SourceItemChunkEntity, chunk_id)

    def get_all(self) -> list[SourceItemChunkEntity]:
        with SessionLocal() as session:
            return (
                session.query(SourceItemChunkEntity)
                .order_by(SourceItemChunkEntity.id)
                .all()
            )