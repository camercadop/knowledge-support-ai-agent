import uuid

from sqlalchemy.orm import Session

from app.application.ports.vector_store import SearchResult, VectorStore
from app.infrastructure.database.models.document_chunk import (
    DocumentChunk as DocumentChunkORM,
)


class PgVectorStore(VectorStore):
    """VectorStore implementation backed by pgvector via SQLAlchemy."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self._db = db

    def upsert(
        self,
        chunk_id: uuid.UUID,
        document_id: uuid.UUID,
        chunk: str,
        embedding: list[float],
    ) -> None:
        """Store or update a chunk with its embedding.

        Inserts a new row if the chunk_id does not exist, otherwise updates
        the embedding and text in place.
        """
        orm = self._db.get(DocumentChunkORM, chunk_id)
        if orm is None:
            orm = DocumentChunkORM(
                id=chunk_id, document_id=document_id, chunk=chunk, embedding=embedding
            )
            self._db.add(orm)
        else:
            orm.chunk = chunk
            orm.embedding = embedding

    def search(self, embedding: list[float], top_k: int = 5) -> list[SearchResult]:
        """Return the top-k chunks closest to the given embedding by cosine distance.

        Results are ordered from most to least similar.
        """
        distance = DocumentChunkORM.embedding.cosine_distance(embedding).label(
            "distance"
        )
        rows = (
            self._db.query(DocumentChunkORM, distance)
            .order_by(distance)
            .limit(top_k)
            .all()
        )
        return [
            SearchResult(
                chunk_id=row.id,
                document_id=row.document_id,
                chunk=row.chunk,
                score=float(dist),
            )
            for row, dist in rows
        ]
