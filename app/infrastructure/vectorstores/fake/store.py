import math
import uuid
from typing import Any

from app.application.support.ports.vector_store import SearchResult, VectorStore


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
        self._documents: dict[uuid.UUID, tuple[str, str | None]] = {}

    def add_document(
        self, document_id: uuid.UUID, title: str, source: str | None = None
    ) -> None:
        """Register document metadata for lookup during search.

        This is a test-only helper that mirrors the documents table in
        PgVectorStore. Call this before upserting chunks that belong to
        the document so search() can populate title and source on results.

        Args:
            document_id: UUID of the document.
            title: Human-readable title of the document.
            source: Optional origin of the document (e.g. file path, URL).
        """
        self._documents[document_id] = (title, source)

    def set_metadata(self, chunk_id: uuid.UUID, metadata: dict[str, Any]) -> None:
        """Attach metadata to an already-upserted chunk.

        This is a test-only helper that mirrors the metadata column stored on
        document_chunks in PgVectorStore. Call this after upserting the chunk
        to enable metadata_filters in search().

        Args:
            chunk_id: UUID of the chunk to update.
            metadata: Key-value pairs to attach to the chunk.
        """
        document_id, chunk, embedding, _ = self._store[chunk_id]
        self._store[chunk_id] = (document_id, chunk, embedding, metadata)

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
        self._store[chunk_id] = (document_id, chunk, embedding, {})

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
                document_title=self._documents.get(document_id, ("", None))[0],
                source=self._documents.get(document_id, ("", None))[1],
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
