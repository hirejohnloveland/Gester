from gester.infrastructure.embeddings.embedding_service import EmbeddingService
from gester.infrastructure.storage.sqlite.source_item_chunk_repository import SourceItemChunkRepository
from gester.infrastructure.storage.vector.qdrant_vector_store import QdrantVectorStore
from gester.infrastructure.storage.sqlite.source_item_repository import SourceItemRepository


class ChunkEmbeddingService:
    def __init__(
        self,
        chunk_repository: SourceItemChunkRepository,
        source_item_repository: SourceItemRepository,
        embedding_service: EmbeddingService,
        vector_store: QdrantVectorStore,
    ) -> None:
        self._chunk_repository = chunk_repository
        self._source_item_repository = source_item_repository
        self._embedding_service = embedding_service
        self._vector_store = vector_store

    def embed_chunks(self, rebuild: bool = False) -> int:
        if rebuild:
            self._vector_store.clear_collection()
            chunks = self._chunk_repository.get_all()
        else:
            chunks = self._chunk_repository.get_unembedded_chunks()

        embedded_count = 0

        for chunk in chunks:
            was_embedded = self._embed_chunk(chunk)

            if was_embedded:
                self._chunk_repository.mark_embedded(chunk.id)
                embedded_count += 1

        return embedded_count

    def _embed_chunk(self, chunk) -> bool:
        source_item = self._source_item_repository.get_by_id(chunk.source_item_id)

        if source_item is None:
            return False

        embedding_text = self._build_embedding_text(source_item, chunk)
        embedding = self._embedding_service.generate_embedding(embedding_text)

        self._vector_store.upsert_chunk_embedding(
            chunk_id=chunk.id,
            source_item_id=source_item.id,
            embedding=embedding,
        )

        return True

    def _build_embedding_text(self, source_item, chunk) -> str:
        return (
            f"Title: {source_item.title}\n"
            f"URL: {source_item.url}\n\n"
            f"{chunk.chunk_text}"
        )