from gester.domain.models.source_item import SourceItem
from gester.infrastructure.storage.sqlite.entities.source_item_entity import SourceItemEntity


def to_domain(entity: SourceItemEntity) -> SourceItem:
    return SourceItem(
        id=entity.id,
        source_type=entity.source_type,
        title=entity.title,
        url=entity.url,
        raw_content=entity.raw_content,
        published_at=entity.published_at,
        created_at=entity.created_at,
    )


def to_entity(model: SourceItem) -> SourceItemEntity:
    entity = SourceItemEntity(
        source_type=model.source_type,
        title=model.title,
        url=model.url,
        raw_content=model.raw_content,
        published_at=model.published_at,
    )

    if model.id is not None:
        entity.id = model.id

    if model.created_at is not None:
        entity.created_at = model.created_at

    return entity
