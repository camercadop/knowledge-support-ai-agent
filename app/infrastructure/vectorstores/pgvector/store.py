import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.application.support.ports.search_strategy import SearchStrategy
from app.application.support.ports.vector_store import SearchResult, VectorStore
from app.infrastructure.database.sqlalchemy.postgresql.models.document import (
    Document as DocumentORM,
)
from app.infrastructure.database.sqlalchemy.postgresql.models.document_chunk import (
    DocumentChunk as DocumentChunkORM,
)


class PgVectorStore(VectorStore):
    """VectorStore implementation backed by pgvector via SQLAlchemy."""

    def __init__(self, db: Session, strategy: SearchStrategy) -> None:
        """Initialize with an active database session and a search strategy.

        Args:
            db: Active SQLAlchemy session for this request.
            strategy: SearchStrategy implementation that controls retrieval mode.
        """
        self._db = db
        self._strategy = strategy

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
        knowledge_base_id: uuid.UUID | None = None,
        metadata_filters: dict[str, str] | None = None,
        query: str | None = None,
    ) -> list[SearchResult]:
        """Return chunks ranked by the active search strategy.

        Delegates entirely to the injected SearchStrategy. The strategy
        controls both context construction and query execution.

        Args:
            embedding: Query vector to search against.
            top_k: Maximum number of results to return.
            min_score: If set, exclude results with a score above this threshold.
            knowledge_base_id: If set, only return chunks belonging to this
                knowledge base. When None, only chunks whose document has no
                knowledge base are returned.
            metadata_filters: If set, only return chunks whose metadata contains
                all specified key-value pairs.
            query: Raw query text forwarded to the strategy.

        Returns:
            List of SearchResult ordered from most to least relevant.
        """
        ctx = self._strategy.build_context(
            embedding=embedding,
            top_k=top_k,
            min_score=min_score,
            knowledge_base_id=knowledge_base_id,
            metadata_filters=metadata_filters,
            query=query,
        )
        return self._strategy.execute(self._base_query, ctx)

    def _base_query(
        self,
        knowledge_base_id: uuid.UUID | None,
        metadata_filters: dict[str, str] | None,
    ) -> Any:
        """Build a base SQLAlchemy query with common JOIN and filters applied.

        Joins document_chunks to documents and applies knowledge_base_id and
        metadata_filters. Callers add their own column expressions and ordering
        on top of this.

        Args:
            knowledge_base_id: If set, filter to chunks whose document belongs
                to this knowledge base. When None, only chunks with no knowledge
                base are returned.
            metadata_filters: If set, apply JSONB containment filter on metadata.

        Returns:
            A SQLAlchemy Query object with JOIN and filters applied.
        """
        q = self._db.query(
            DocumentChunkORM,
            DocumentORM.title,
            DocumentORM.source,
            DocumentORM.knowledge_base_id,
        ).join(DocumentORM, DocumentChunkORM.document_id == DocumentORM.id)

        if knowledge_base_id is not None:
            q = q.filter(DocumentORM.knowledge_base_id == knowledge_base_id)
        else:
            q = q.filter(DocumentORM.knowledge_base_id.is_(None))

        if metadata_filters is not None:
            q = q.filter(DocumentChunkORM.metadata_.op("@>")(metadata_filters))

        return q
