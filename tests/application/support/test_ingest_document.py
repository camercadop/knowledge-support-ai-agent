import pytest
from sqlalchemy.orm import Session

from app.application.support.ingest_document import IngestDocument
from app.infrastructure.ai.chunking.fixed_size import FixedSizeChunkStrategy
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
        chunk_strategy=FixedSizeChunkStrategy(chunk_size=500, chunk_overlap=50),
    )


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
