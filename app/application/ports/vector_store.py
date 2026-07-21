import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class SearchResult:
    """A single result from a vector similarity search."""

    chunk_id: uuid.UUID
    document_id: uuid.UUID
    chunk: str
    score: float


class VectorStore(ABC):
    """Port that defines the contract for vector store providers.

    Implementations live in infrastructure/vectorstores/.
    """

    @abstractmethod
    def upsert(
        self,
        chunk_id: uuid.UUID,
        document_id: uuid.UUID,
        chunk: str,
        embedding: list[float],
    ) -> None:
        """Store or update a chunk with its embedding.

        Args:
            chunk_id: UUID of the document chunk.
            document_id: UUID of the parent document.
            chunk: The text content of the chunk.
            embedding: The vector embedding for the chunk.
        """

    @abstractmethod
    def search(self, embedding: list[float], top_k: int = 5) -> list[SearchResult]:
        """Return the top-k chunks closest to the given embedding.

        Args:
            embedding: Query vector to search against.
            top_k: Maximum number of results to return.

        Returns:
            List of SearchResult ordered from most to least similar.
        """
