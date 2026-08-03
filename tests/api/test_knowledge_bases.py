import uuid
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.application.support.models.knowledge_base import KnowledgeBase
from app.infrastructure.database.sqlalchemy.postgresql.engine import get_db
from app.main import app

_KB_ID = uuid.uuid4()
_MOCK_KB = KnowledgeBase(id=_KB_ID, name="Support", description="Support KB")
_MOCK_CRUD = MagicMock()
_MOCK_CRUD.create.return_value = _MOCK_KB
_MOCK_CRUD.list.return_value = [_MOCK_KB]
_MOCK_CRUD.get_by_id.return_value = _MOCK_KB
_MOCK_CRUD.update.return_value = _MOCK_KB
_MOCK_CRUD.delete.return_value = None


@pytest.fixture()
def client() -> Generator[TestClient]:
    app.dependency_overrides[get_db] = lambda: None
    with patch(
        "app.container.support.SupportContainer.knowledge_base_crud",
        return_value=_MOCK_CRUD,
    ):
        yield TestClient(app)
    app.dependency_overrides.clear()


# --- POST /knowledge-bases ---


def test_create_knowledge_base_returns_201(client: TestClient) -> None:
    response = client.post("/knowledge-bases", json={"name": "Support"})
    assert response.status_code == 201


def test_create_knowledge_base_returns_name_and_id(client: TestClient) -> None:
    response = client.post("/knowledge-bases", json={"name": "Support"})
    body = response.json()
    assert body["name"] == "Support"
    assert "id" in body


def test_create_knowledge_base_missing_name_returns_422(client: TestClient) -> None:
    response = client.post("/knowledge-bases", json={})
    assert response.status_code == 422


# --- GET /knowledge-bases ---


def test_list_knowledge_bases_returns_200(client: TestClient) -> None:
    response = client.get("/knowledge-bases")
    assert response.status_code == 200


def test_list_knowledge_bases_returns_list(client: TestClient) -> None:
    response = client.get("/knowledge-bases")
    assert isinstance(response.json(), list)


# --- GET /knowledge-bases/{id} ---


def test_get_knowledge_base_returns_200(client: TestClient) -> None:
    response = client.get(f"/knowledge-bases/{_KB_ID}")
    assert response.status_code == 200


def test_get_knowledge_base_returns_correct_id(client: TestClient) -> None:
    response = client.get(f"/knowledge-bases/{_KB_ID}")
    assert response.json()["id"] == str(_KB_ID)


def test_get_knowledge_base_not_found_returns_404(client: TestClient) -> None:
    _MOCK_CRUD.get_by_id.return_value = None
    response = client.get(f"/knowledge-bases/{uuid.uuid4()}")
    assert response.status_code == 404
    _MOCK_CRUD.get_by_id.return_value = _MOCK_KB


# --- PATCH /knowledge-bases/{id} ---


def test_update_knowledge_base_returns_200(client: TestClient) -> None:
    response = client.patch(
        f"/knowledge-bases/{_KB_ID}", json={"name": "Updated"}
    )
    assert response.status_code == 200


def test_update_knowledge_base_not_found_returns_404(client: TestClient) -> None:
    _MOCK_CRUD.get_by_id.return_value = None
    response = client.patch(
        f"/knowledge-bases/{uuid.uuid4()}", json={"name": "Updated"}
    )
    assert response.status_code == 404
    _MOCK_CRUD.get_by_id.return_value = _MOCK_KB


# --- DELETE /knowledge-bases/{id} ---


def test_delete_knowledge_base_returns_204(client: TestClient) -> None:
    response = client.delete(f"/knowledge-bases/{_KB_ID}")
    assert response.status_code == 204


def test_delete_knowledge_base_not_found_returns_404(client: TestClient) -> None:
    _MOCK_CRUD.get_by_id.return_value = None
    response = client.delete(f"/knowledge-bases/{uuid.uuid4()}")
    assert response.status_code == 404
    _MOCK_CRUD.get_by_id.return_value = _MOCK_KB
