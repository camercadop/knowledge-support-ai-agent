import uuid

import pytest
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.infrastructure.database.sqlalchemy.postgresql.models.document import (
    Document as DocumentORM,
)
from app.infrastructure.database.sqlalchemy.postgresql.models.document_chunk import (
    DocumentChunk as DocumentChunkORM,
)
from app.infrastructure.vectorstores.pgvector.store import PgVectorStore

_DIMS = settings.embedding_dimensions or 1536
_EMBEDDING = [0.0] * _DIMS


@pytest.fixture()
def store(pg_db: Session) -> PgVectorStore:
    """Return a PgVectorStore backed by the PostgreSQL session."""
    return PgVectorStore(pg_db)


def _seed(
    db: Session,
    title: str,
    source: str | None,
    chunk: str,
    embedding: list[float] | None = None,
) -> tuple[uuid.UUID, uuid.UUID]:
    """Persist a document and one chunk, returning (document_id, chunk_id)."""
    doc = DocumentORM(title=title, source=source, content=chunk)
    db.add(doc)
    db.flush()
    chunk_orm = DocumentChunkORM(
        document_id=doc.id,
        chunk=chunk,
        embedding=embedding or _EMBEDDING,
    )
    db.add(chunk_orm)
    db.flush()
    return doc.id, chunk_orm.id


# --- search ---


def test_search_returns_document_title_and_source(
    store: PgVectorStore, pg_db: Session
) -> None:
    _seed(pg_db, "My Doc", "https://example.com", "hello")
    results = store.search(_EMBEDDING)
    assert len(results) == 1
    assert results[0].document_title == "My Doc"
    assert results[0].source == "https://example.com"


def test_search_returns_none_source_when_not_set(
    store: PgVectorStore, pg_db: Session
) -> None:
    _seed(pg_db, "My Doc", None, "hello")
    results = store.search(_EMBEDDING)
    assert len(results) == 1
    assert results[0].source is None


def test_search_returns_correct_chunk_and_document_ids(
    store: PgVectorStore, pg_db: Session
) -> None:
    doc_id, chunk_id = _seed(pg_db, "My Doc", None, "hello")
    results = store.search(_EMBEDDING)
    assert results[0].chunk_id == chunk_id
    assert results[0].document_id == doc_id


def test_search_orders_by_score_ascending(
    store: PgVectorStore, pg_db: Session
) -> None:
    _seed(pg_db, "Near Doc", None, "near", embedding=[1.0] + [0.0] * (_DIMS - 1))
    _seed(pg_db, "Far Doc", None, "far", embedding=[0.0] * (_DIMS - 1) + [1.0])
    results = store.search([1.0] + [0.0] * (_DIMS - 1))
    assert results[0].chunk == "near"
    assert results[1].chunk == "far"
