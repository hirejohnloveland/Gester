from gester.domain.models.source_item_chunk import SourceItemChunk
from gester.infrastructure.storage.sqlite.entities.source_item_chunk_entity import (
    SourceItemChunkEntity,
)


def to_domain(entity: SourceItemChunkEntity) -> SourceItemChunk:
    return SourceItemChunk(
        id=entity.id,
        source_item_id=entity.source_item_id,
        embedded_at=entity.embedded_at,
        chunk_index=entity.chunk_index,
        chunk_text=entity.chunk_text,
        char_start=entity.char_start,
        char_end=entity.char_end,
        created_at=entity.created_at,
    )


def to_entity(model: SourceItemChunk) -> SourceItemChunkEntity:
    entity = SourceItemChunkEntity(
        source_item_id=model.source_item_id,
        embedded_at=model.embedded_at,
        chunk_index=model.chunk_index,
        chunk_text=model.chunk_text,
        char_start=model.char_start,
        char_end=model.char_end,
    )

    if model.id is not None:
        entity.id = model.id

    if model.created_at is not None:
        entity.created_at = model.created_at

    return entity
