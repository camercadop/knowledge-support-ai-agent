from sqlalchemy.orm import Session

from app.application.ports.repositories.document import AbstractDocumentRepository
from app.application.ports.repositories.document_chunk import AbstractDocumentChunkRepository
from app.application.ports.unit_of_work.knowledge import KnowledgeUnitOfWork
from app.infrastructure.database.sqlalchemy.repositories.document import DocumentRepository
from app.infrastructure.database.sqlalchemy.repositories.document_chunk import DocumentChunkRepository


class SqlAlchemyKnowledgeUnitOfWork(KnowledgeUnitOfWork):
    """KnowledgeUnitOfWork backed by a SQLAlchemy session."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self._db = db
        self._documents = DocumentRepository(db)
        self._document_chunks = DocumentChunkRepository(db)

    @property
    def documents(self) -> AbstractDocumentRepository:
        """Return the document repository bound to the current session."""
        return self._documents

    @property
    def document_chunks(self) -> AbstractDocumentChunkRepository:
        """Return the document chunk repository bound to the current session."""
        return self._document_chunks

    def commit(self) -> None:
        """Commit the current session transaction."""
        self._db.commit()
