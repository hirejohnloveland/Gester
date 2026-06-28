from gester.application.ingestion.text_chunking_service import TextChunkingService
from gester.domain.models.source_item_chunk import SourceItemChunk
from gester.infrastructure.storage.sqlite.source_item_chunk_repository import SourceItemChunkRepository
from gester.infrastructure.storage.sqlite.source_item_repository import SourceItemRepository
from gester.infrastructure.storage.vector.qdrant_vector_store import QdrantVectorStore


class SourceItemChunkingService:
    def __init__(
        self,
        source_item_repository: SourceItemRepository,
        chunk_repository: SourceItemChunkRepository,
        chunking_service: TextChunkingService,
        vector_store: QdrantVectorStore,
    ) -> None:
        self._source_item_repository = source_item_repository
        self._chunk_repository = chunk_repository
        self._chunking_service = chunking_service
        self._vector_store = vector_store

    def chunk_missing_source_items(self) -> int:
        source_items = self._source_item_repository.get_all_with_content()

        chunked_item_count = 0

        for source_item in source_items:
            if self._chunk_repository.exists_for_source_item_id(source_item.id):
                continue

            chunks = self._chunking_service.chunk(source_item.raw_content)

            for index, chunk in enumerate(chunks):
                source_item_chunk = SourceItemChunk(
                    source_item_id=source_item.id,
                    chunk_index=index,
                    chunk_text=chunk.chunk_text,
                    char_start=chunk.char_start,
                    char_end=chunk.char_end,
                )

                self._chunk_repository.add(source_item_chunk)

            chunked_item_count += 1

        return chunked_item_count

    def reset_chunks(self) -> int:
        deleted_chunk_count = self._chunk_repository.delete_all()
        self._vector_store.clear_collection()

        return deleted_chunk_count
