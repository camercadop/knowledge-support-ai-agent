from abc import abstractmethod

from app.application.shared.ports.unit_of_work import UnitOfWork
from app.application.support.ports.repositories.document import (
    AbstractDocumentRepository,
)
from app.application.support.ports.repositories.document_chunk import (
    AbstractDocumentChunkRepository,
)
from app.application.support.ports.repositories.knowledge_base import (
    AbstractKnowledgeBaseRepository,
)


class KnowledgeUnitOfWork(UnitOfWork):
    """Port that defines the transactional boundary for the knowledge domain.

    Exposes document, document chunk, and knowledge base repositories
    within a single transaction.
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

    @property
    @abstractmethod
    def knowledge_bases(self) -> AbstractKnowledgeBaseRepository:
        """Return the knowledge base repository bound to the current transaction."""
