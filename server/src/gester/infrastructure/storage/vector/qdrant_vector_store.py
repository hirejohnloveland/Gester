from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams


class QdrantVectorStore:
    def __init__(self) -> None:
        self._collection_name = "gester_chunks"

        project_root = Path(__file__).resolve().parents[6]
        qdrant_path = project_root / "data" / "qdrant"

        self._client = QdrantClient(path=str(qdrant_path))

    def ensure_collection(self) -> None:
        if self._client.collection_exists(self._collection_name):
            return

        self._client.create_collection(
            collection_name=self._collection_name,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE,
            ),
        )

    def upsert_chunk_embedding(
        self,
        chunk_id: int,
        source_item_id: int,
        embedding: list[float],
    ) -> None:
        self.ensure_collection()

        point = PointStruct(
            id=chunk_id,
            vector=embedding,
            payload={
                "chunk_id": chunk_id,
                "source_item_id": source_item_id,
            },
        )

        self._client.upsert(
            collection_name=self._collection_name,
            points=[point],
        )

        
    def search(self, embedding: list[float], limit: int = 5):
        self.ensure_collection()

        response = self._client.query_points(
            collection_name=self._collection_name,
            query=embedding,
            limit=limit,
        )

        return response.points