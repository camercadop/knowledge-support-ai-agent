from abc import ABC, abstractmethod

from app.application.ports.repositories.document import AbstractDocumentRepository
from app.application.ports.repositories.document_chunk import (
    AbstractDocumentChunkRepository,
)


class KnowledgeUnitOfWork(ABC):
    """Port that defines the transactional boundary for the knowledge domain.

    Exposes document and document chunk repositories within a single transaction.
    Implementations live in infrastructure/database/unit_of_work/.
    """

    @property
    @abstractmethod
    def documents(self) -> AbstractDocumentRepository:
        """Return the document repository bound to the current transaction."""

    @property
    @abstractmethod
    def document_chunks(self) -> AbstractDocumentChunkRepository:
        """Return the document chunk repository bound to the current transaction."""

    @abstractmethod
    def commit(self) -> None:
        """Persist all changes made within the current transaction."""
