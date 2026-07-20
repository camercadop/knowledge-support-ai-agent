import uuid

from sqlalchemy.orm import Session

from app.infrastructure.database.models.document_chunk import DocumentChunk


class DocumentChunkRepository:
    """Handles persistence and similarity search for DocumentChunk entities."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self._db = db

    def create(
        self,
        document_id: uuid.UUID,
        chunk: str,
        embedding: list[float],
    ) -> DocumentChunk:
        """Persist a new document chunk with its embedding and return it."""
        entity = DocumentChunk(
            document_id=document_id,
            chunk=chunk,
            embedding=embedding,
        )
        self._db.add(entity)
        self._db.flush()
        return entity

    def search_similar(
        self,
        embedding: list[float],
        top_k: int = 5,
    ) -> list[DocumentChunk]:
        """Return the top-k chunks closest to the given embedding by cosine distance.

        Results are ordered from most to least similar. Use top_k to control
        how many results are returned.
        """
        return (
            self._db.query(DocumentChunk)
            .order_by(DocumentChunk.embedding.cosine_distance(embedding))
            .limit(top_k)
            .all()
        )
