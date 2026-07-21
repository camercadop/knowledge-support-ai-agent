import uuid

from sqlalchemy.orm import Session

from app.application.models.document import Document
from app.application.ports.repositories.document import AbstractDocumentRepository
from app.infrastructure.database.sqlalchemy.postgresql.models.document import (
    Document as DocumentORM,
)


class DocumentRepository(AbstractDocumentRepository):
    """Handles persistence operations for Document entities."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self._db = db

    def create(self, title: str, source: str | None, content: str) -> Document:
        """Persist a new document and return it.

        Args:
            title: Human-readable title of the document.
            source: Optional origin of the document (e.g. file path, URL).
            content: Full raw text content of the document.

        Returns:
            The persisted Document.
        """
        orm = DocumentORM(title=title, source=source, content=content)
        self._db.add(orm)
        self._db.flush()
        return Document(
            id=orm.id, title=orm.title, source=orm.source, content=orm.content
        )

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
            id=orm.id, title=orm.title, source=orm.source, content=orm.content
        )
