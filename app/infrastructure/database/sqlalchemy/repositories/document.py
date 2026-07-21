import uuid

from sqlalchemy.orm import Session

from app.application.models.document import Document
from app.application.ports.repositories.document import AbstractDocumentRepository
from app.infrastructure.database.sqlalchemy.models.document import Document as DocumentORM


class DocumentRepository(AbstractDocumentRepository):
    """Handles persistence operations for Document entities."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self._db = db

    def create(self, title: str, source: str | None, content: str) -> Document:
        """Persist a new document and return it."""
        orm = DocumentORM(title=title, source=source, content=content)
        self._db.add(orm)
        self._db.flush()
        return Document(
            id=orm.id, title=orm.title, source=orm.source, content=orm.content
        )

    def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        """Return the document with the given id, or None if not found."""
        orm = self._db.query(DocumentORM).filter(DocumentORM.id == document_id).first()
        if orm is None:
            return None
        return Document(
            id=orm.id, title=orm.title, source=orm.source, content=orm.content
        )
