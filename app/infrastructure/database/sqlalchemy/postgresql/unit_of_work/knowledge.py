from sqlalchemy.orm import Session

from app.application.support.ports.repositories.document import (
    AbstractDocumentRepository,
)
from app.application.support.ports.repositories.document_chunk import (
    AbstractDocumentChunkRepository,
)
from app.application.support.ports.repositories.knowledge_base import (
    AbstractKnowledgeBaseRepository,
)
from app.application.support.ports.unit_of_work.knowledge import KnowledgeUnitOfWork
from app.infrastructure.database.sqlalchemy.postgresql.repositories.document import (
    DocumentRepository,
)
from app.infrastructure.database.sqlalchemy.postgresql.repositories.document_chunk import (  # noqa: E501
    DocumentChunkRepository,
)
from app.infrastructure.database.sqlalchemy.postgresql.repositories.knowledge_base import (  # noqa: E501
    KnowledgeBaseRepository,
)


class SqlAlchemyKnowledgeUnitOfWork(KnowledgeUnitOfWork):
    """KnowledgeUnitOfWork backed by a SQLAlchemy session."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self._db = db
        self._documents = DocumentRepository(db)
        self._document_chunks = DocumentChunkRepository(db)
        self._knowledge_bases = KnowledgeBaseRepository(db)

    @property
    def documents(self) -> AbstractDocumentRepository:
        """Return the document repository bound to the current session."""
        return self._documents

    @property
    def document_chunks(self) -> AbstractDocumentChunkRepository:
        """Return the document chunk repository bound to the current session."""
        return self._document_chunks

    @property
    def knowledge_bases(self) -> AbstractKnowledgeBaseRepository:
        """Return the knowledge base repository bound to the current session."""
        return self._knowledge_bases

    def commit(self) -> None:
        """Commit the current session transaction."""
        self._db.commit()
