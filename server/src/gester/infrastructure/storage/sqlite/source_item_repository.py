from sqlalchemy import select

from gester.infrastructure.storage.sqlite.entities.source_item_entity import SourceItemEntity
from gester.infrastructure.storage.sqlite.sqlite_db import SessionLocal


class SourceItemRepository:
    def add(self, item: SourceItemEntity) -> SourceItemEntity:
        with SessionLocal() as session:
            session.add(item)
            session.commit()
            session.refresh(item)

            return item

    def get_all(self) -> list[SourceItemEntity]:
        with SessionLocal() as session:
            statement = select(SourceItemEntity).order_by(SourceItemEntity.created_at.desc())
            results = session.scalars(statement).all()

            return list(results)

    def get_by_url(self, url: str) -> SourceItemEntity | None:
        with SessionLocal() as session:
            statement = select(SourceItemEntity).where(SourceItemEntity.url == url)
            result = session.scalars(statement).first()

            return result

    def add_if_not_exists(self, item: SourceItemEntity) -> SourceItemEntity | None:
        if item.url is None or item.url.strip() == "":
            return None
        with SessionLocal() as session:
            existing = session.scalars(
                select(SourceItemEntity).where(SourceItemEntity.url == item.url)
            ).first()

            if existing is not None:
                return None

            session.add(item)
            session.commit()
            session.refresh(item)

            return item
    
    def get_all_with_content(self) -> list[SourceItemEntity]:
        with SessionLocal() as session:
            statement = select(SourceItemEntity).where(
                SourceItemEntity.raw_content.is_not(None)
            )

            return list(session.scalars(statement).all())
    
    def get_by_id(self, source_item_id: int) -> SourceItemEntity | None:
        with SessionLocal() as session:
            return session.get(SourceItemEntity, source_item_id)