import math
import uuid
from typing import Any

from app.application.ports.vector_store import SearchResult, VectorStore


def _cosine_distance(a: list[float], b: list[float]) -> float:
    """Return cosine distance between two vectors (0 = identical, 2 = opposite).

    Args:
        a: First vector.
        b: Second vector.

    Returns:
        Cosine distance as a float between 0.0 and 2.0.
    """
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
        self._store: dict[
            uuid.UUID, tuple[uuid.UUID, str, list[float], dict[str, Any]]
        ] = {}

    def upsert(
        self,
        chunk_id: uuid.UUID,
        document_id: uuid.UUID,
        chunk: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Store or replace a chunk and its embedding by chunk_id.

        Args:
            chunk_id: UUID of the document chunk.
            document_id: UUID of the parent document.
            chunk: The text content of the chunk.
            embedding: The vector embedding for the chunk.
            metadata: Optional key-value metadata for filtering.
        """
        self._store[chunk_id] = (document_id, chunk, embedding, metadata or {})

    def search(
        self,
        embedding: list[float],
        top_k: int = 5,
        min_score: float | None = None,
        metadata_filters: dict[str, str] | None = None,
    ) -> list[SearchResult]:
        """Return the top-k chunks closest to the given embedding by cosine distance.

        Applies optional min_score and metadata_filters in memory.

        Args:
            embedding: Query vector to search against.
            top_k: Maximum number of results to return.
            min_score: If set, exclude results with a score above this threshold.
            metadata_filters: If set, only return chunks whose metadata contains
                all specified key-value pairs.

        Returns:
            List of SearchResult ordered from most to least similar.
        """
        candidates = [
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
                meta,
            ) in self._store.items()
            if (
                min_score is None
                or _cosine_distance(embedding, stored_embedding) <= min_score
            )
            and (
                metadata_filters is None
                or all(meta.get(k) == v for k, v in metadata_filters.items())
            )
        ]
        return sorted(candidates, key=lambda r: r.score)[:top_k]
