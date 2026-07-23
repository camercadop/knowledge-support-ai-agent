import uuid

import pytest

from app.infrastructure.vectorstores.fake.store import FakeVectorStore, _cosine_distance

# --- _cosine_distance ---


def test_cosine_distance_identical_vectors() -> None:
    assert _cosine_distance([1.0, 0.0], [1.0, 0.0]) == pytest.approx(0.0)


def test_cosine_distance_orthogonal_vectors() -> None:
    assert _cosine_distance([1.0, 0.0], [0.0, 1.0]) == pytest.approx(1.0)


def test_cosine_distance_opposite_vectors() -> None:
    assert _cosine_distance([1.0, 0.0], [-1.0, 0.0]) == pytest.approx(2.0)


def test_cosine_distance_zero_vector_returns_one() -> None:
    assert _cosine_distance([0.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)


# --- FakeVectorStore ---


def _chunk_id() -> uuid.UUID:
    return uuid.uuid4()


def _doc_id() -> uuid.UUID:
    return uuid.uuid4()


def test_search_returns_empty_when_store_is_empty() -> None:
    store = FakeVectorStore()
    assert store.search([1.0, 0.0]) == []


def test_search_returns_inserted_chunk() -> None:
    store = FakeVectorStore()
    cid = _chunk_id()
    store.upsert(
        chunk_id=cid, document_id=_doc_id(), chunk="hello", embedding=[1.0, 0.0]
    )
    results = store.search([1.0, 0.0])
    assert len(results) == 1
    assert results[0].chunk == "hello"
    assert results[0].chunk_id == cid


def test_search_orders_by_score_ascending() -> None:
    store = FakeVectorStore()
    store.upsert(
        chunk_id=_chunk_id(), document_id=_doc_id(), chunk="far", embedding=[0.0, 1.0]
    )
    store.upsert(
        chunk_id=_chunk_id(), document_id=_doc_id(), chunk="near", embedding=[1.0, 0.0]
    )
    results = store.search([1.0, 0.0])
    assert results[0].chunk == "near"
    assert results[1].chunk == "far"


def test_search_respects_top_k() -> None:
    store = FakeVectorStore()
    for _ in range(5):
        store.upsert(
            chunk_id=_chunk_id(), document_id=_doc_id(), chunk="x", embedding=[1.0, 0.0]
        )
    assert len(store.search([1.0, 0.0], top_k=3)) == 3


def test_upsert_overwrites_existing_chunk() -> None:
    store = FakeVectorStore()
    cid = _chunk_id()
    store.upsert(
        chunk_id=cid, document_id=_doc_id(), chunk="original", embedding=[1.0, 0.0]
    )
    store.upsert(
        chunk_id=cid, document_id=_doc_id(), chunk="updated", embedding=[1.0, 0.0]
    )
    results = store.search([1.0, 0.0])
    assert len(results) == 1
    assert results[0].chunk == "updated"


def test_search_excludes_results_above_min_score() -> None:
    store = FakeVectorStore()
    store.upsert(
        chunk_id=_chunk_id(), document_id=_doc_id(), chunk="near", embedding=[1.0, 0.0]
    )
    store.upsert(
        chunk_id=_chunk_id(), document_id=_doc_id(), chunk="far", embedding=[0.0, 1.0]
    )
    results = store.search([1.0, 0.0], min_score=0.1)
    assert len(results) == 1
    assert results[0].chunk == "near"


def test_search_filters_by_metadata() -> None:
    store = FakeVectorStore()
    store.upsert(
        chunk_id=_chunk_id(),
        document_id=_doc_id(),
        chunk="match",
        embedding=[1.0, 0.0],
        metadata={"lang": "en"},
    )
    store.upsert(
        chunk_id=_chunk_id(),
        document_id=_doc_id(),
        chunk="no-match",
        embedding=[1.0, 0.0],
        metadata={"lang": "es"},
    )
    results = store.search([1.0, 0.0], metadata_filters={"lang": "en"})
    assert len(results) == 1
    assert results[0].chunk == "match"
