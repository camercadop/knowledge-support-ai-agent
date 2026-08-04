import uuid

import pytest
from collections.abc import Generator
from sqlalchemy.orm import Session

from app.application.support.models.document import Document
from app.infrastructure.database.sqlalchemy.postgresql.repositories.document import (
    DocumentRepository,
)


@pytest.fixture()
def repo(pg_db: Session) -> DocumentRepository:
    return DocumentRepository(pg_db)


def test_create_returns_document_with_all_fields(repo: DocumentRepository) -> None:
    kb_id = uuid.uuid4()
    doc = repo.create(
        title="Test Doc",
        source="manual",
        content="some content",
        embedding_model_used="text-embedding-3-small",
        knowledge_base_id=kb_id,
    )

    assert doc.id is not None
    assert doc.title == "Test Doc"
    assert doc.source == "manual"
    assert doc.content == "some content"
    assert doc.embedding_model_used == "text-embedding-3-small"
    assert doc.knowledge_base_id == kb_id


def test_create_assigns_id(repo: DocumentRepository) -> None:
    doc = repo.create(
        title="Test Doc",
        source=None,
        content="some content",
    )
    assert doc.id is not None


def test_create_with_none_source(repo: DocumentRepository) -> None:
    doc = repo.create(
        title="Test Doc",
        source=None,
        content="some content",
    )
    assert doc.source is None


def test_create_with_none_embedding_model(repo: DocumentRepository) -> None:
    doc = repo.create(
        title="Test Doc",
        source="manual",
        content="some content",
        embedding_model_used=None,
    )
    assert doc.embedding_model_used is None


def test_create_persists_knowledge_base_id(repo: DocumentRepository) -> None:
    kb_id = uuid.uuid4()
    doc = repo.create(
        title="Test Doc",
        source=None,
        content="some content",
        knowledge_base_id=kb_id,
    )
    assert doc.knowledge_base_id == kb_id


def test_get_by_title_and_source_found(repo: DocumentRepository) -> None:
    kb_id = uuid.uuid4()
    repo.create(
        title="Found Doc",
        source="manual",
        content="some content",
        knowledge_base_id=kb_id,
    )

    result = repo.get_by_title_and_source("Found Doc", "manual")

    assert result is not None
    assert result.title == "Found Doc"
    assert result.source == "manual"
    assert result.knowledge_base_id == kb_id


def test_get_by_title_and_source_not_found(repo: DocumentRepository) -> None:
    result = repo.get_by_title_and_source("Nonexistent", "manual")
    assert result is None


def test_get_by_title_and_source_with_none_source(repo: DocumentRepository) -> None:
    repo.create(
        title="No Source Doc",
        source=None,
        content="some content",
    )

    result = repo.get_by_title_and_source("No Source Doc", None)

    assert result is not None
    assert result.title == "No Source Doc"


def test_get_by_id_found(repo: DocumentRepository) -> None:
    doc = repo.create(
        title="ById Doc",
        source=None,
        content="some content",
    )

    result = repo.get_by_id(doc.id)

    assert result is not None
    assert result.title == "ById Doc"


def test_get_by_id_not_found(repo: DocumentRepository) -> None:
    result = repo.get_by_id(uuid.uuid4())
    assert result is None


def test_delete_existing_document(repo: DocumentRepository) -> None:
    doc = repo.create(
        title="To Delete",
        source=None,
        content="some content",
    )

    repo.delete(doc.id)

    result = repo.get_by_id(doc.id)
    assert result is None


def test_delete_nonexistent_document(repo: DocumentRepository) -> None:
    repo.delete(uuid.uuid4())