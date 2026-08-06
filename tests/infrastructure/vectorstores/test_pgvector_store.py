import uuid
from unittest.mock import MagicMock, call

from app.infrastructure.database.sqlalchemy.postgresql.models.document_chunk import (
    DocumentChunk,
)
from app.infrastructure.vectorstores.search_strategies.strategies import (
    HybridSearchStrategy,
    VectorSearchStrategy,
)
from app.infrastructure.vectorstores.pgvector.store import PgVectorStore

_DOC_ID = uuid.uuid4()
_CHUNK_ID = uuid.uuid4()
_KB_ID = uuid.uuid4()
_EMBEDDING = [0.0] * 1536


def _store() -> tuple[PgVectorStore, MagicMock]:
    db = MagicMock()
    return PgVectorStore(db, VectorSearchStrategy(MagicMock())), db


def _make_row(
    chunk: str = "hello",
    chunk_id: uuid.UUID | None = None,
    doc_id: uuid.UUID | None = None,
    title: str = "Doc",
    source: str | None = None,
    kb_id: uuid.UUID | None = None,
    dist: float = 0.1,
) -> tuple[MagicMock, str, str | None, uuid.UUID | None, float]:
    orm = MagicMock()
    orm.id = chunk_id or _CHUNK_ID
    orm.document_id = doc_id or _DOC_ID
    orm.chunk = chunk
    return orm, title, source, kb_id, dist


def _mock_query(db: MagicMock, rows: list) -> MagicMock:
    """Wire db.query(...).join(...).add_columns(...).order_by(...).filter(...).limit(...).all() chain."""
    chain = MagicMock()
    chain.join.return_value = chain
    chain.add_columns.return_value = chain
    chain.order_by.return_value = chain
    chain.filter.return_value = chain
    chain.limit.return_value = MagicMock(all=MagicMock(return_value=rows))
    db.query.return_value = chain
    return chain


def test_upsert_adds_new_chunk_when_not_found() -> None:
    store, db = _store()
    db.get.return_value = None

    store.upsert(chunk_id=_CHUNK_ID, document_id=_DOC_ID, chunk="hello", embedding=_EMBEDDING)

    db.add.assert_called_once()
    added: DocumentChunk = db.add.call_args[0][0]
    assert added.id == _CHUNK_ID
    assert added.chunk == "hello"
    assert added.document_id == _DOC_ID


def test_upsert_updates_existing_chunk_when_found() -> None:
    store, db = _store()
    existing = DocumentChunk(
        id=_CHUNK_ID, document_id=_DOC_ID, chunk="old", embedding=_EMBEDDING
    )
    db.get.return_value = existing

    store.upsert(chunk_id=_CHUNK_ID, document_id=_DOC_ID, chunk="new", embedding=_EMBEDDING)

    db.add.assert_not_called()
    assert existing.chunk == "new"


def test_upsert_does_not_call_add_on_update() -> None:
    store, db = _store()
    db.get.return_value = DocumentChunk(
        id=_CHUNK_ID, document_id=_DOC_ID, chunk="x", embedding=_EMBEDDING
    )

    store.upsert(chunk_id=_CHUNK_ID, document_id=_DOC_ID, chunk="y", embedding=_EMBEDDING)

    db.add.assert_not_called()


def test_upsert_stores_metadata_on_insert() -> None:
    store, db = _store()
    db.get.return_value = None

    store.upsert(
        chunk_id=_CHUNK_ID,
        document_id=_DOC_ID,
        chunk="hello",
        embedding=_EMBEDDING,
        metadata={"lang": "en"},
    )

    db.add.assert_called_once()
    added: DocumentChunk = db.add.call_args[0][0]
    assert added.metadata_ == {"lang": "en"}


def test_upsert_updates_metadata_on_existing_chunk() -> None:
    store, db = _store()
    existing = DocumentChunk(
        id=_CHUNK_ID, document_id=_DOC_ID, chunk="old", embedding=_EMBEDDING
    )
    db.get.return_value = existing

    store.upsert(
        chunk_id=_CHUNK_ID,
        document_id=_DOC_ID,
        chunk="old",
        embedding=_EMBEDDING,
        metadata={"lang": "es"},
    )

    db.add.assert_not_called()
    assert existing.metadata_ == {"lang": "es"}


# --- search (unit) ---


def test_search_returns_mapped_search_results() -> None:
    store, db = _store()
    chain = _mock_query(db, [_make_row(chunk="hello", dist=0.2)])

    results = store.search(_EMBEDDING)

    assert len(results) == 1
    assert results[0].chunk == "hello"
    assert results[0].score == 0.2
    assert results[0].chunk_id == _CHUNK_ID
    assert results[0].document_id == _DOC_ID


def test_search_returns_empty_list_when_no_rows() -> None:
    store, db = _store()
    _mock_query(db, [])

    assert store.search(_EMBEDDING) == []


def test_search_applies_top_k_limit() -> None:
    store, db = _store()
    chain = _mock_query(db, [])

    store.search(_EMBEDDING, top_k=3)

    chain.limit.assert_called_once_with(3)


def test_search_applies_min_score_filter_when_provided() -> None:
    store, db = _store()
    chain = _mock_query(db, [])

    store.search(_EMBEDDING, min_score=0.5)

    # filter must have been called at least once (for min_score + knowledge_base_id=None)
    assert chain.filter.call_count >= 1


def test_search_does_not_apply_min_score_filter_when_none() -> None:
    store, db = _store()
    chain = _mock_query(db, [])

    store.search(_EMBEDDING, min_score=None)

    # only the knowledge_base_id IS NULL filter is applied
    assert chain.filter.call_count == 1


def test_search_applies_knowledge_base_id_filter_when_provided() -> None:
    store, db = _store()
    chain = _mock_query(db, [])

    store.search(_EMBEDDING, knowledge_base_id=_KB_ID)

    assert chain.filter.call_count >= 1


def test_search_applies_metadata_filters_when_provided() -> None:
    store, db = _store()
    chain = _mock_query(db, [])

    store.search(_EMBEDDING, metadata_filters={"lang": "en"})

    # min_score absent → 1 (kb IS NULL) + 1 (metadata) = 2
    assert chain.filter.call_count == 2


def test_search_maps_knowledge_base_id_on_result() -> None:
    store, db = _store()
    _mock_query(db, [_make_row(kb_id=_KB_ID)])

    results = store.search(_EMBEDDING)

    assert results[0].knowledge_base_id == _KB_ID


def test_search_maps_none_source_on_result() -> None:
    store, db = _store()
    _mock_query(db, [_make_row(source=None)])

    results = store.search(_EMBEDDING)

    assert results[0].source is None


def test_search_maps_document_title_on_result() -> None:
    store, db = _store()
    _mock_query(db, [_make_row(title="My Doc")])

    results = store.search(_EMBEDDING)

    assert results[0].document_title == "My Doc"


# --- hybrid search dispatch ---


def _mock_hybrid_query(db: MagicMock, vector_rows: list, fts_rows: list) -> None:
    """Wire db.query chain to return different rows for vector and FTS legs."""
    chain = MagicMock()
    chain.join.return_value = chain
    chain.add_columns.return_value = chain
    chain.order_by.return_value = chain
    chain.filter.return_value = chain
    chain.limit.side_effect = [
        MagicMock(all=MagicMock(return_value=vector_rows)),
        MagicMock(all=MagicMock(return_value=fts_rows)),
    ]
    db.query.return_value = chain


def _hybrid_store() -> tuple[PgVectorStore, MagicMock]:
    db = MagicMock()
    mock_settings = MagicMock(
        retrieval_hybrid_fts_language="english", retrieval_hybrid_rrf_k=60
    )
    return PgVectorStore(db, HybridSearchStrategy(mock_settings)), db


def test_search_dispatches_to_vector_search_when_no_query() -> None:
    store, db = _store()
    chain = _mock_query(db, [_make_row()])

    store.search(_EMBEDDING, query=None)

    chain.limit.assert_called_once_with(5)


def test_search_dispatches_to_hybrid_search_when_query_provided() -> None:
    store, db = _hybrid_store()
    row = _make_row()
    _mock_hybrid_query(db, vector_rows=[row], fts_rows=[row])

    results = store.search(_EMBEDDING, query="test")

    assert len(results) == 1


def test_hybrid_search_returns_rrf_score_greater_than_zero() -> None:
    store, db = _hybrid_store()
    row = _make_row()
    _mock_hybrid_query(db, vector_rows=[row], fts_rows=[row])

    results = store.search(_EMBEDDING, query="test")

    assert results[0].score > 0.0


def test_hybrid_search_deduplicates_chunks_appearing_in_both_legs() -> None:
    store, db = _hybrid_store()
    row = _make_row()
    _mock_hybrid_query(db, vector_rows=[row], fts_rows=[row])

    results = store.search(_EMBEDDING, query="test")

    assert len(results) == 1


def test_hybrid_search_includes_chunks_from_fts_only() -> None:
    store, db = _hybrid_store()
    vector_row = _make_row(chunk="vector only", chunk_id=uuid.uuid4())
    fts_row = _make_row(chunk="fts only", chunk_id=uuid.uuid4())
    _mock_hybrid_query(db, vector_rows=[vector_row], fts_rows=[fts_row])

    results = store.search(_EMBEDDING, query="test")

    chunks = {r.chunk for r in results}
    assert "vector only" in chunks
    assert "fts only" in chunks
