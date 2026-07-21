from collections.abc import Generator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

import app.api.chat as chat_module
from app.infrastructure.ai.mock.chat import MockChatModel
from app.infrastructure.ai.mock.embeddings import MockEmbeddingModel
from app.infrastructure.database.engine import get_db
from app.main import app


@pytest.fixture()
def client() -> Generator[TestClient]:
    """Return a TestClient with AI models replaced by mocks and DB bypassed."""
    chat_module._chat_model = MockChatModel(reply="mock reply")
    chat_module._embedding_model = MockEmbeddingModel()

    app.dependency_overrides[get_db] = lambda: None

    with patch("app.api.chat.AnswerQuestion.handle", return_value="mock reply"):
        yield TestClient(app)

    app.dependency_overrides.clear()


def test_chat_returns_reply(client: TestClient) -> None:
    """POST /chat returns 200 with the assistant reply."""
    response = client.post("/chat", json={"phone": "+1234567890", "message": "Hi"})
    assert response.status_code == 200
    assert response.json() == {"reply": "mock reply"}


def test_chat_missing_fields(client: TestClient) -> None:
    """POST /chat with a missing field returns 422."""
    response = client.post("/chat", json={"phone": "+1234567890"})
    assert response.status_code == 422


def test_chat_empty_message(client: TestClient) -> None:
    """POST /chat with an empty message still returns a reply."""
    response = client.post("/chat", json={"phone": "+1234567890", "message": ""})
    assert response.status_code == 200
    assert "reply" in response.json()
