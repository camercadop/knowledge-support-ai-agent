import math
import uuid

from app.application.ports.vector_store import SearchResult, VectorStore


def _cosine_distance(a: list[float], b: list[float]) -> float:
    """Return cosine distance between two vectors (0 = identical, 2 = opposite)."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 1.0
    return 1.0 - dot / (norm_a * norm_b)


class FakeVectorStore(VectorStore):
    """In-memory VectorStore for use in tests and local development.

    Stores chunks in a plain dict and computes cosine distance on search.
    Not suitable for production.
    """

    def __init__(self) -> None:
        """Initialize with an empty in-memory store."""
        self._store: dict[uuid.UUID, tuple[uuid.UUID, str, list[float]]] = {}

    def upsert(
        self,
        chunk_id: uuid.UUID,
        document_id: uuid.UUID,
        chunk: str,
        embedding: list[float],
    ) -> None:
        """Store or replace a chunk and its embedding by chunk_id.

        Args:
            chunk_id: UUID of the document chunk.
            document_id: UUID of the parent document.
            chunk: The text content of the chunk.
            embedding: The vector embedding for the chunk.
        """
        self._store[chunk_id] = (document_id, chunk, embedding)

    def search(self, embedding: list[float], top_k: int = 5) -> list[SearchResult]:
        """Return the top-k chunks closest to the given embedding by cosine distance.

        Args:
            embedding: Query vector to search against.
            top_k: Maximum number of results to return.

        Returns:
            List of SearchResult ordered from most to least similar.
        """
        results = sorted(
            (
                SearchResult(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    chunk=chunk,
                    score=_cosine_distance(embedding, stored_embedding),
                )
                for chunk_id, (
                    document_id,
                    chunk,
                    stored_embedding,
                ) in self._store.items()
            ),
            key=lambda r: r.score,
        )
        return results[:top_k]
