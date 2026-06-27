from gester.domain.models.source_item_chunk import SourceItemChunk
from gester.infrastructure.storage.sqlite.source_item_chunk_repository import SourceItemChunkRepository


class SourceItemChunkQueryService:
    def __init__(self) -> None:
        self._repository = SourceItemChunkRepository()

    def get_by_source_item_id(self, source_item_id: int) -> list[SourceItemChunk]:
        return self._repository.get_by_source_item_id(source_item_id)
