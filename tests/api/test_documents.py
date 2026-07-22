import uuid
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.application.models.document import Document
from app.infrastructure.database.sqlalchemy.postgresql.engine import get_db
from app.main import app

_DOCUMENT_ID = uuid.uuid4()
_MOCK_DOCUMENT = Document(
    id=_DOCUMENT_ID, title="My Doc", source="manual", content="..."
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
