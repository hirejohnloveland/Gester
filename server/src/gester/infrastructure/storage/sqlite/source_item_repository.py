from sqlalchemy import select

from gester.domain.models.source_item import SourceItem
from gester.infrastructure.storage.sqlite.entities.source_item_entity import SourceItemEntity
from gester.infrastructure.storage.sqlite.mappers import source_item_mapper
from gester.infrastructure.storage.sqlite.sqlite_db import SessionLocal


class SourceItemRepository:
    def add(self, item: SourceItem) -> SourceItem:
        with SessionLocal() as session:
            entity = source_item_mapper.to_entity(item)
            session.add(entity)
            session.commit()
            session.refresh(entity)

            return source_item_mapper.to_domain(entity)

    def get_all(self) -> list[SourceItem]:
        with SessionLocal() as session:
            statement = select(SourceItemEntity).order_by(SourceItemEntity.created_at.desc())
            results = session.scalars(statement).all()

            return [source_item_mapper.to_domain(entity) for entity in results]

    def get_by_url(self, url: str) -> SourceItem | None:
        with SessionLocal() as session:
            statement = select(SourceItemEntity).where(SourceItemEntity.url == url)
            result = session.scalars(statement).first()

            if result is None:
                return None

            return source_item_mapper.to_domain(result)

    def add_if_not_exists(self, item: SourceItem) -> SourceItem | None:
        if item.url is None or item.url.strip() == "":
            return None

        with SessionLocal() as session:
            existing = session.scalars(
                select(SourceItemEntity).where(SourceItemEntity.url == item.url)
            ).first()

            if existing is not None:
                return None

            entity = source_item_mapper.to_entity(item)
            session.add(entity)
            session.commit()
            session.refresh(entity)

            return source_item_mapper.to_domain(entity)

    def get_all_with_content(self) -> list[SourceItem]:
        with SessionLocal() as session:
            statement = select(SourceItemEntity).where(
                SourceItemEntity.raw_content.is_not(None)
            )

            return [
                source_item_mapper.to_domain(entity)
                for entity in session.scalars(statement).all()
            ]

    def get_by_id(self, source_item_id: int) -> SourceItem | None:
        with SessionLocal() as session:
            entity = session.get(SourceItemEntity, source_item_id)

            if entity is None:
                return None

            return source_item_mapper.to_domain(entity)
