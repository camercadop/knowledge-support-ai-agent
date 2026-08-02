import uuid
from abc import ABC, abstractmethod

from app.application.support.models.document import Document


class AbstractDocumentRepository(ABC):
    """Port that defines the contract for document persistence."""

    @abstractmethod
    def create(
        self,
        title: str,
        source: str | None,
        content: str,
        embedding_model_used: str | None = None,
    ) -> Document:
        """Persist a new document and return it."""

    @abstractmethod
    def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        """Return the document with the given id, or None if not found."""

    @abstractmethod
    def get_by_title_and_source(
        self, title: str, source: str | None
    ) -> Document | None:
        """Return the document matching title and source, or None if not found."""

    @abstractmethod
    def delete(self, document_id: uuid.UUID) -> None:
        """Delete the document."""
