import uuid
from abc import ABC, abstractmethod

from app.application.models.document import Document


class AbstractDocumentRepository(ABC):
    """Port that defines the contract for document persistence."""

    @abstractmethod
    def create(self, title: str, source: str | None, content: str) -> Document:
        """Persist a new document and return it."""

    @abstractmethod
    def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        """Return the document with the given id, or None if not found."""
