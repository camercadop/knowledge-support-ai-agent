from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.application.support.answer_question import AnswerResult
from app.infrastructure.database.sqlalchemy.postgresql.engine import get_db
from app.main import app

_MOCK_DB = MagicMock()
_MOCK_USE_CASE = MagicMock()
_MOCK_USE_CASE.handle.return_value = AnswerResult(reply="mock reply", chunks=None)


@pytest.fixture()
def client() -> Generator[TestClient]:
    app.dependency_overrides[get_db] = lambda: _MOCK_DB

    with patch(
        "app.container.support.SupportContainer.answer_question",
        return_value=_MOCK_USE_CASE,
    ):
        yield TestClient(app)

    app.dependency_overrides.clear()


def test_chat_returns_reply(client: TestClient) -> None:
    """POST /chat returns 200 with the assistant reply."""
    response = client.post("/chat", json={"phone": "+1234567890", "message": "Hi"})
    assert response.status_code == 200
    assert response.json() == {"reply": "mock reply", "chunks": None}


def test_chat_missing_fields(client: TestClient) -> None:
    """POST /chat with a missing field returns 422."""
    response = client.post("/chat", json={"phone": "+1234567890"})
    assert response.status_code == 422


def test_chat_empty_message(client: TestClient) -> None:
    """POST /chat with an empty message returns 422."""
    response = client.post("/chat", json={"phone": "+1234567890", "message": ""})
    assert response.status_code == 422
