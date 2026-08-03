import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.application.support.ports.vector_store import SearchResult, VectorStore
from app.infrastructure.database.sqlalchemy.postgresql.models.document import (
    Document as DocumentORM,
)
from app.infrastructure.database.sqlalchemy.postgresql.models.document_chunk import (
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
        metadata: dict[str, str] | None = None,
    ) -> None:
        """Store or update a chunk with its embedding.

        Inserts a new row if the chunk_id does not exist, otherwise updates
        the embedding and text in place. Document metadata (title, source) is
        fetched from the documents table at query time via a JOIN in search().
        """
        orm = self._db.get(DocumentChunkORM, chunk_id)
        if orm is None:
            orm = DocumentChunkORM(
                id=chunk_id,
                document_id=document_id,
                chunk=chunk,
                embedding=embedding,
                metadata_=metadata or {},
            )
            self._db.add(orm)
        else:
            orm.chunk = chunk
            orm.embedding = embedding
            orm.metadata_ = metadata or {}

    def search(
        self,
        embedding: list[float],
        top_k: int = 5,
        min_score: float | None = None,
        metadata_filters: dict[str, str] | None = None,
    ) -> list[SearchResult]:
        """Return the top-k chunks closest to the given embedding by cosine distance.

        Applies an optional maximum distance filter (min_score) and optional
        JSONB containment filter on metadata. Results are ordered from most to
        least similar.
        """
        distance = DocumentChunkORM.embedding.cosine_distance(embedding).label(
            "distance"
        )
        query = (
            self._db.query(
                DocumentChunkORM,
                DocumentORM.title,
                DocumentORM.source,
                distance,
            )
            .join(DocumentORM, DocumentChunkORM.document_id == DocumentORM.id)
            .order_by(distance)
        )

        if min_score is not None:
            query = query.filter(distance <= min_score)

        if metadata_filters is not None:
            filters: dict[str, Any] = metadata_filters
            query = query.filter(
                DocumentChunkORM.metadata_.cast(type_=None).op("@>")(filters)
            )

        rows = query.limit(top_k).all()
        return [
            SearchResult(
                chunk_id=row.id,
                document_id=row.document_id,
                chunk=row.chunk,
                score=float(dist),
                document_title=title,
                source=source,
            )
            for row, title, source, dist in rows
        ]
