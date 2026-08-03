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


def test_search_top_k_limits_results(store: PgVectorStore, pg_db: Session) -> None:
    for i in range(4):
        _seed(pg_db, f"Doc {i}", None, f"chunk {i}")
    results = store.search(_EMBEDDING, top_k=2)
    assert len(results) == 2


def test_search_min_score_excludes_distant_chunks(
    store: PgVectorStore, pg_db: Session
) -> None:
    _seed(pg_db, "Near", None, "near", embedding=[1.0] + [0.0] * (_DIMS - 1))
    _seed(pg_db, "Far", None, "far", embedding=[0.0] * (_DIMS - 1) + [1.0])
    # cosine distance between [1,0,...] and [0,...,1] is 1.0; strict threshold excludes it
    results = store.search([1.0] + [0.0] * (_DIMS - 1), min_score=0.5)
    assert all(r.score <= 0.5 for r in results)
    chunks = [r.chunk for r in results]
    assert "near" in chunks
    assert "far" not in chunks


def test_search_min_score_none_returns_all_chunks(
    store: PgVectorStore, pg_db: Session
) -> None:
    _seed(pg_db, "Near", None, "near", embedding=[1.0] + [0.0] * (_DIMS - 1))
    _seed(pg_db, "Far", None, "far", embedding=[0.0] * (_DIMS - 1) + [1.0])
    results = store.search([1.0] + [0.0] * (_DIMS - 1), min_score=None)
    assert len(results) == 2


def test_search_knowledge_base_id_filters_by_kb(
    store: PgVectorStore, pg_db: Session
) -> None:
    kb_id = uuid.uuid4()
    doc_in = DocumentORM(title="In KB", source=None, content="in", knowledge_base_id=kb_id)
    doc_out = DocumentORM(title="Out KB", source=None, content="out", knowledge_base_id=None)
    pg_db.add_all([doc_in, doc_out])
    pg_db.flush()
    for doc in (doc_in, doc_out):
        pg_db.add(DocumentChunkORM(document_id=doc.id, chunk=doc.content, embedding=_EMBEDDING))
    pg_db.flush()

    results = store.search(_EMBEDDING, knowledge_base_id=kb_id)
    assert len(results) == 1
    assert results[0].chunk == "in"
    assert results[0].knowledge_base_id == kb_id


def test_search_no_knowledge_base_id_excludes_kb_docs(
    store: PgVectorStore, pg_db: Session
) -> None:
    kb_id = uuid.uuid4()
    doc_kb = DocumentORM(title="KB Doc", source=None, content="kb", knowledge_base_id=kb_id)
    doc_none = DocumentORM(title="No KB", source=None, content="none")
    pg_db.add_all([doc_kb, doc_none])
    pg_db.flush()
    for doc in (doc_kb, doc_none):
        pg_db.add(DocumentChunkORM(document_id=doc.id, chunk=doc.content, embedding=_EMBEDDING))
    pg_db.flush()

    results = store.search(_EMBEDDING)
    chunks = [r.chunk for r in results]
    assert "none" in chunks
    assert "kb" not in chunks


def test_search_metadata_filters_returns_matching_chunks(
    store: PgVectorStore, pg_db: Session
) -> None:
    doc = DocumentORM(title="Doc", source=None, content="text")
    pg_db.add(doc)
    pg_db.flush()
    pg_db.add(
        DocumentChunkORM(
            document_id=doc.id, chunk="en chunk", embedding=_EMBEDDING, metadata_={"lang": "en"}
        )
    )
    pg_db.add(
        DocumentChunkORM(
            document_id=doc.id, chunk="es chunk", embedding=_EMBEDDING, metadata_={"lang": "es"}
        )
    )
    pg_db.flush()

    results = store.search(_EMBEDDING, metadata_filters={"lang": "en"})
    assert len(results) == 1
    assert results[0].chunk == "en chunk"


def test_search_metadata_filters_no_match_returns_empty(
    store: PgVectorStore, pg_db: Session
) -> None:
    doc = DocumentORM(title="Doc", source=None, content="text")
    pg_db.add(doc)
    pg_db.flush()
    pg_db.add(
        DocumentChunkORM(
            document_id=doc.id, chunk="chunk", embedding=_EMBEDDING, metadata_={"lang": "en"}
        )
    )
    pg_db.flush()

    results = store.search(_EMBEDDING, metadata_filters={"lang": "fr"})
    assert results == []
