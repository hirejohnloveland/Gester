from gester.infrastructure.embeddings.embedding_service import EmbeddingService
from gester.infrastructure.storage.sqlite.source_item_chunk_repository import SourceItemChunkRepository
from gester.infrastructure.storage.vector.qdrant_vector_store import QdrantVectorStore


class ChunkEmbeddingService:
    def __init__(self) -> None:
        self._chunk_repository = SourceItemChunkRepository()
        self._embedding_service = EmbeddingService()
        self._vector_store = QdrantVectorStore()

    def embed_missing_chunks(self) -> int:
        chunks = self._chunk_repository.get_unembedded_chunks()

        embedded_count = 0

        for chunk in chunks:
            embedding = self._embedding_service.generate_embedding(chunk.chunk_text)

            self._vector_store.upsert_chunk_embedding(
                chunk_id=chunk.id,
                source_item_id=chunk.source_item_id,
                embedding=embedding,
            )

            self._chunk_repository.mark_embedded(chunk.id)
            embedded_count += 1

        return embedded_count