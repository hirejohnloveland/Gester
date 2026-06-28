from gester.application.responses.search_result_response import SearchResultResponse
from gester.infrastructure.embeddings.embedding_service import EmbeddingService
from gester.infrastructure.storage.sqlite.source_item_chunk_repository import SourceItemChunkRepository
from gester.infrastructure.storage.sqlite.source_item_repository import SourceItemRepository
from gester.infrastructure.storage.vector.qdrant_vector_store import QdrantVectorStore


class SearchService:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: QdrantVectorStore,
        chunk_repository: SourceItemChunkRepository,
        source_item_repository: SourceItemRepository,
    ) -> None:
        self._embedding_service = embedding_service
        self._vector_store = vector_store
        self._chunk_repository = chunk_repository
        self._source_item_repository = source_item_repository

    def search(self, query: str, limit: int = 5,     min_score: float = 0.0,
        dedupe_by_article: bool = True) -> list[SearchResultResponse]:
        
        query_embedding = self._embedding_service.generate_embedding(query)

        search_limit = limit * 4 if dedupe_by_article else limit
        hits = self._vector_store.search(query_embedding, search_limit)

        results: list[SearchResultResponse] = []
        seen_source_item_ids: set[int] = set()

        for hit in hits:
            if hit.score < min_score:
                continue

            chunk_id = hit.payload["chunk_id"]
            source_item_id = hit.payload["source_item_id"]


            chunk = self._chunk_repository.get_by_id(chunk_id)
            source_item = self._source_item_repository.get_by_id(source_item_id)

            if dedupe_by_article and source_item.id in seen_source_item_ids:
                continue
            if chunk is None or source_item is None:
                continue

            results.append(
                SearchResultResponse(
                    score=hit.score,
                    chunk_id=chunk.id,
                    source_item_id=source_item.id,
                    title=source_item.title,
                    url=source_item.url,
                    chunk_text=chunk.chunk_text,
                )
            )

            seen_source_item_ids.add(source_item_id)

        return results