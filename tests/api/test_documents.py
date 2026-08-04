import uuid
import uuid
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.application.support.models.document import Document
from app.infrastructure.database.sqlalchemy.postgresql.engine import get_db
from app.main import app

_DOCUMENT_ID = uuid.uuid4()
_MOCK_DOCUMENT = Document(
    id=_DOCUMENT_ID,
    title="My Doc",
    source="manual",
    content="...",
    embedding_model_used="text-embedding-3-small",
    knowledge_base_id=None,
)
_MOCK_USE_CASE = MagicMock()
_MOCK_USE_CASE.handle.return_value = _MOCK_DOCUMENT


@pytest.fixture()
def client() -> Generator[TestClient]:
    app.dependency_overrides[get_db] = lambda: None

    with patch(
        "app.container.support.SupportContainer.ingest_document",
        return_value=_MOCK_USE_CASE,
    ):
        yield TestClient(app)

    app.dependency_overrides.clear()


def test_ingest_document_returns_200(client: TestClient) -> None:
    """POST /documents returns 200 with id, title, and source."""
    response = client.post(
        "/documents",
        json={"title": "My Doc", "source": "manual", "content": "some content"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "My Doc"
    assert body["source"] == "manual"
    assert "id" in body


def test_ingest_document_missing_content_returns_422(client: TestClient) -> None:
    """POST /documents without content returns 422."""
    response = client.post("/documents", json={"title": "My Doc"})
    assert response.status_code == 422


def test_ingest_document_with_knowledge_base_id(
    client: TestClient,
) -> None:
    """POST /documents with knowledge_base_id returns it in response."""
    kb_id = str(uuid.uuid4())
    mock_doc = Document(
        id=uuid.uuid4(),
        title="My Doc",
        source="manual",
        content="some content",
        embedding_model_used="text-embedding-3-small",
        knowledge_base_id=uuid.UUID(kb_id),
    )
    mock_use_case = MagicMock()
    mock_use_case.handle.return_value = mock_doc
    with patch(
        "app.container.support.SupportContainer.ingest_document",
        return_value=mock_use_case,
    ):
        response = client.post(
            "/documents",
            json={
                "title": "My Doc",
                "source": "manual",
                "content": "some content",
                "knowledge_base_id": kb_id,
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["knowledge_base_id"] == kb_id


def test_ingest_document_missing_title_returns_422(client: TestClient) -> None:
    """POST /documents without title returns 422."""
    response = client.post("/documents", json={"content": "some content"})
    assert response.status_code == 422


def test_ingest_document_source_is_optional(client: TestClient) -> None:
    """POST /documents without source still returns 200."""
    response = client.post(
        "/documents",
        json={"title": "My Doc", "content": "some content"},
    )
    assert response.status_code == 200


def test_ingest_document_metadata_is_optional(client: TestClient) -> None:
    """POST /documents without metadata still returns 200."""
    response = client.post(
        "/documents",
        json={"title": "My Doc", "content": "some content"},
    )
    assert response.status_code == 200


def test_ingest_document_content_at_max_length_returns_200(client: TestClient) -> None:
    """POST /documents with content exactly at 100,000 chars returns 200."""
    response = client.post(
        "/documents",
        json={"title": "My Doc", "content": "a" * 100_000},
    )
    assert response.status_code == 200


def test_ingest_document_content_exceeds_max_length_returns_422(client: TestClient) -> None:
    """POST /documents with content exceeding 100,000 chars returns 422."""
    response = client.post(
        "/documents",
        json={"title": "My Doc", "content": "a" * 100_001},
    )
    assert response.status_code == 422


def test_ingest_document_accepts_metadata(client: TestClient) -> None:
    """POST /documents with metadata returns 200."""
    response = client.post(
        "/documents",
        json={
            "title": "My Doc",
            "content": "some content",
            "metadata": {"lang": "en", "dept": "HR"},
        },
    )
    assert response.status_code == 200
