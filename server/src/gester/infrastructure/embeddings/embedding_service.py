from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self) -> None:
        self._model = SentenceTransformer(
            "BAAI/bge-small-en-v1.5"
        )

    def generate_embedding(self, text: str) -> list[float]:
        embedding = self._model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()