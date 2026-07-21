import pytest
from sqlalchemy.orm import Session

from app.application.support.ingest_document import IngestDocument, _chunk_text
from app.infrastructure.ai.mock.embeddings import MockEmbeddingModel
from app.infrastructure.database.sqlalchemy.postgresql.unit_of_work.knowledge import (
    SqlAlchemyKnowledgeUnitOfWork,
)
from app.infrastructure.vectorstores.fake.store import FakeVectorStore


@pytest.fixture()
def uow(db: Session) -> SqlAlchemyKnowledgeUnitOfWork:
    """Return a KnowledgeUnitOfWork backed by the in-memory SQLite session."""
    return SqlAlchemyKnowledgeUnitOfWork(db)


@pytest.fixture()
def vector_store() -> FakeVectorStore:
    """Return an empty FakeVectorStore."""
    return FakeVectorStore()


def _make_use_case(
    uow: SqlAlchemyKnowledgeUnitOfWork,
    vector_store: FakeVectorStore,
) -> IngestDocument:
    return IngestDocument(
        uow=uow,
        embedding_model=MockEmbeddingModel(),
        vector_store=vector_store,
    )


# --- _chunk_text ---


def test_chunk_text_single_chunk_when_content_fits() -> None:
    chunks = _chunk_text("short")
    assert chunks == ["short"]


def test_chunk_text_splits_into_overlapping_chunks() -> None:
    content = "a" * 600
    chunks = _chunk_text(content)
    assert len(chunks) == 2
    assert len(chunks[0]) == 500
    # second chunk starts at 500 - 50 = 450, so length is 150
    assert chunks[1] == content[450:]


def test_chunk_text_overlap_is_shared_between_consecutive_chunks() -> None:
    content = "a" * 1000
    chunks = _chunk_text(content)
    # last 50 chars of chunk[0] == first 50 chars of chunk[1]
    assert chunks[0][-50:] == chunks[1][:50]


# --- IngestDocument.handle ---


def test_returns_document_with_correct_title_and_source(
    uow: SqlAlchemyKnowledgeUnitOfWork, vector_store: FakeVectorStore
) -> None:
    doc = _make_use_case(uow, vector_store).handle("My Doc", "manual", "some content")
    assert doc.title == "My Doc"
    assert doc.source == "manual"


def test_returns_document_with_none_source(
    uow: SqlAlchemyKnowledgeUnitOfWork, vector_store: FakeVectorStore
) -> None:
    doc = _make_use_case(uow, vector_store).handle("My Doc", None, "some content")
    assert doc.source is None


def test_persists_document_retrievable_by_id(
    uow: SqlAlchemyKnowledgeUnitOfWork, vector_store: FakeVectorStore
) -> None:
    doc = _make_use_case(uow, vector_store).handle("My Doc", "manual", "some content")
    persisted = uow.documents.get_by_id(doc.id)
    assert persisted is not None
    assert persisted.id == doc.id


def test_upserts_chunks_into_vector_store(
    uow: SqlAlchemyKnowledgeUnitOfWork, vector_store: FakeVectorStore
) -> None:
    content = "a" * 600  # produces 2 chunks
    _make_use_case(uow, vector_store).handle("Doc", None, content)
    results = vector_store.search([0.0, 0.0, 0.0])
    assert len(results) == 2


def test_single_chunk_for_short_content(
    uow: SqlAlchemyKnowledgeUnitOfWork, vector_store: FakeVectorStore
) -> None:
    _make_use_case(uow, vector_store).handle("Doc", None, "short content")
    results = vector_store.search([0.0, 0.0, 0.0])
    assert len(results) == 1
    assert results[0].chunk == "short content"
