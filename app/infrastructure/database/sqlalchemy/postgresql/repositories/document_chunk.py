import uuid

from sqlalchemy.orm import Session

from app.application.models.document_chunk import DocumentChunk
from app.application.ports.repositories.document_chunk import (
    AbstractDocumentChunkRepository,
)
from app.infrastructure.database.sqlalchemy.postgresql.models.document_chunk import (
    DocumentChunk as DocumentChunkORM,
)


class DocumentChunkRepository(AbstractDocumentChunkRepository):
    """Handles persistence operations for DocumentChunk entities."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self._db = db

    def create(
        self, document_id: uuid.UUID, chunk: str, embedding: list[float]
    ) -> DocumentChunk:
        """Persist a new document chunk with its embedding and return it.

        Args:
            document_id: UUID of the parent document.
            chunk: The text content of the chunk.
            embedding: The vector embedding for the chunk.

        Returns:
            The persisted DocumentChunk.
        """
        orm = DocumentChunkORM(
            document_id=document_id, chunk=chunk, embedding=embedding
        )
        self._db.add(orm)
        self._db.flush()
        return DocumentChunk(id=orm.id, document_id=orm.document_id, chunk=orm.chunk)
