import uuid

from sqlalchemy.orm import Session

from app.application.support.models.document import Document
from app.application.support.ports.repositories.document import (
    AbstractDocumentRepository,
)
from app.infrastructure.database.sqlalchemy.postgresql.models.document import (
    Document as DocumentORM,
)


class DocumentRepository(AbstractDocumentRepository):
    """Handles persistence operations for Document entities."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self._db = db

    def create(
        self,
        title: str,
        source: str | None,
        content: str,
        embedding_model_used: str | None = None,
        knowledge_base_id: uuid.UUID | None = None,
    ) -> Document:
        """Persist a new document and return it.

        Args:
            title: Human-readable title of the document.
            source: Optional origin of the document (e.g. file path, URL).
            content: Full raw text content of the document.
            embedding_model_used: Identifier of the embedding model used
                when this document was ingested.
            knowledge_base_id: Optional knowledge base this document belongs to.

        Returns:
            The persisted Document.
        """
        orm = DocumentORM(
            title=title,
            source=source,
            content=content,
            embedding_model_used=embedding_model_used,
            knowledge_base_id=knowledge_base_id,
        )
        self._db.add(orm)
        self._db.flush()
        return Document(
            id=orm.id,
            title=orm.title,
            source=orm.source,
            content=orm.content,
            embedding_model_used=orm.embedding_model_used,
            knowledge_base_id=orm.knowledge_base_id,
        )

    def get_by_title_and_source(
        self, title: str, source: str | None
    ) -> Document | None:
        """Return the document matching title and source, or None if not found."""
        orm = (
            self._db.query(DocumentORM)
            .filter(DocumentORM.title == title, DocumentORM.source == source)
            .first()
        )
        if orm is None:
            return None
        return Document(
            id=orm.id,
            title=orm.title,
            source=orm.source,
            content=orm.content,
            embedding_model_used=orm.embedding_model_used,
            knowledge_base_id=orm.knowledge_base_id,
        )

    def delete(self, document_id: uuid.UUID) -> None:
        """Delete the document and all its chunks (cascade via FK)."""
        orm = self._db.get(DocumentORM, document_id)
        if orm is not None:
            self._db.delete(orm)
            self._db.flush()

    def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        """Return the document with the given id, or None if not found.

        Args:
            document_id: UUID of the document to retrieve.

        Returns:
            The matching Document, or None if it does not exist.
        """
        orm = self._db.query(DocumentORM).filter(DocumentORM.id == document_id).first()
        if orm is None:
            return None
        return Document(
            id=orm.id,
            title=orm.title,
            source=orm.source,
            content=orm.content,
            embedding_model_used=orm.embedding_model_used,
            knowledge_base_id=orm.knowledge_base_id,
        )
