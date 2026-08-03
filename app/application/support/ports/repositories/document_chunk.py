import uuid
from abc import ABC, abstractmethod

from app.application.support.models.document_chunk import DocumentChunk


class AbstractDocumentChunkRepository(ABC):
    """Port that defines the contract for document chunk persistence."""

    @abstractmethod
    def create(
        self,
        document_id: uuid.UUID,
        chunk: str,
        embedding: list[float],
        metadata: dict[str, str] | None = None,
    ) -> DocumentChunk:
        """Persist a new document chunk with its embedding and return it."""
