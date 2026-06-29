"""Standalone chunking stage of the ingestion pipeline.

Chunks source items already stored in SQLite without re-fetching external
content. Used to backfill missing chunks or re-chunk after settings change.
"""

import logging

from gester.application.ingestion.text_chunking_service import TextChunkingService
from gester.domain.models.source_item_chunk import SourceItemChunk
from gester.infrastructure.storage.sqlite.source_item_chunk_repository import SourceItemChunkRepository
from gester.infrastructure.storage.sqlite.source_item_repository import SourceItemRepository
from gester.infrastructure.storage.vector.qdrant_vector_store import QdrantVectorStore

logger = logging.getLogger(__name__)


class SourceItemChunkingService:
    """Chunks stored source items that do not yet have chunk rows."""

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
        """Chunk every source item that has content but no chunks yet.

        Returns the number of source items newly chunked.
        """
        logger.info("Chunking run started for source items missing chunks")

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

            logger.debug(
                "Created %d chunk(s) for source item %d", len(chunks), source_item.id
            )

        logger.info("Chunking run finished; %d item(s) chunked", chunked_item_count)

        return chunked_item_count

    def reset_chunks(self) -> int:
        """Delete all chunks from SQLite and clear the vector store.

        Returns the number of chunk rows deleted.
        """
        deleted_chunk_count = self._chunk_repository.delete_all()
        self._vector_store.clear_collection()

        logger.info("Reset chunks; %d chunk(s) deleted", deleted_chunk_count)

        return deleted_chunk_count
