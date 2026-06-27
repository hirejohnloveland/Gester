from datetime import datetime, timezone

from sqlalchemy import delete, select, update

from gester.domain.models.source_item_chunk import SourceItemChunk
from gester.infrastructure.storage.sqlite.entities.source_item_chunk_entity import (
    SourceItemChunkEntity,
)
from gester.infrastructure.storage.sqlite.mappers import source_item_chunk_mapper
from gester.infrastructure.storage.sqlite.sqlite_db import SessionLocal


class SourceItemChunkRepository:
    def add(self, chunk: SourceItemChunk) -> SourceItemChunk:
        with SessionLocal() as session:
            entity = source_item_chunk_mapper.to_entity(chunk)
            session.add(entity)
            session.commit()
            session.refresh(entity)

            return source_item_chunk_mapper.to_domain(entity)

    def get_by_source_item_id(
        self,
        source_item_id: int,
    ) -> list[SourceItemChunk]:
        with SessionLocal() as session:
            statement = (
                select(SourceItemChunkEntity)
                .where(SourceItemChunkEntity.source_item_id == source_item_id)
                .order_by(SourceItemChunkEntity.chunk_index)
            )

            return [
                source_item_chunk_mapper.to_domain(entity)
                for entity in session.scalars(statement).all()
            ]

    def exists_for_source_item_id(self, source_item_id: int) -> bool:
        with SessionLocal() as session:
            statement = select(SourceItemChunkEntity.id).where(
                SourceItemChunkEntity.source_item_id == source_item_id
            )

            return session.scalars(statement).first() is not None

    def get_unembedded_chunks(self) -> list[SourceItemChunk]:
        with SessionLocal() as session:
            statement = (
                select(SourceItemChunkEntity)
                .where(SourceItemChunkEntity.embedded_at.is_(None))
                .order_by(SourceItemChunkEntity.id)
            )

            return [
                source_item_chunk_mapper.to_domain(entity)
                for entity in session.scalars(statement).all()
            ]

    def mark_embedded(self, chunk_id: int) -> None:
        with SessionLocal() as session:
            statement = (
                update(SourceItemChunkEntity)
                .where(SourceItemChunkEntity.id == chunk_id)
                .values(embedded_at=datetime.now(timezone.utc))
            )

            session.execute(statement)
            session.commit()

    def get_by_id(self, chunk_id: int) -> SourceItemChunk | None:
        with SessionLocal() as session:
            entity = session.get(SourceItemChunkEntity, chunk_id)

            if entity is None:
                return None

            return source_item_chunk_mapper.to_domain(entity)

    def get_all(self) -> list[SourceItemChunk]:
        with SessionLocal() as session:
            statement = select(SourceItemChunkEntity).order_by(SourceItemChunkEntity.id)

            return [
                source_item_chunk_mapper.to_domain(entity)
                for entity in session.scalars(statement).all()
            ]

    def delete_all(self) -> int:
        with SessionLocal() as session:
            result = session.execute(delete(SourceItemChunkEntity))
            session.commit()

            return result.rowcount
