import uuid
from collections.abc import Generator
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.application.analytics.models.rag_interaction_log import RagInteractionLog
from app.infrastructure.database.sqlalchemy.postgresql.engine import get_db
from app.main import app

_MOCK_DB = MagicMock()
_LOG_ID = uuid.uuid4()
_CONV_ID = uuid.uuid4()

_MOCK_LOG = RagInteractionLog(
    id=_LOG_ID,
    conversation_id=_CONV_ID,
    question="what is X?",
    answer="X is Y.",
    model_used="mock-model",
    chunks=None,
    prompt_tokens=10,
    completion_tokens=5,
    created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
)

_MOCK_USE_CASE = MagicMock()
_MOCK_USE_CASE.handle.return_value = [_MOCK_LOG]


@pytest.fixture()
def client() -> Generator[TestClient]:
    app.dependency_overrides[get_db] = lambda: _MOCK_DB
    with patch(
        "app.container.support.SupportContainer.export_rag_interactions",
        return_value=_MOCK_USE_CASE,
    ):
        yield TestClient(app)
    app.dependency_overrides.clear()


def test_list_rag_interactions_returns_200(client: TestClient) -> None:
    response = client.get("/analytics/rag-interactions")
    assert response.status_code == 200


def test_list_rag_interactions_returns_list(client: TestClient) -> None:
    response = client.get("/analytics/rag-interactions")
    assert isinstance(response.json(), list)


def test_list_rag_interactions_returns_correct_fields(client: TestClient) -> None:
    response = client.get("/analytics/rag-interactions")
    body = response.json()[0]
    assert body["id"] == str(_LOG_ID)
    assert body["conversation_id"] == str(_CONV_ID)
    assert body["question"] == "what is X?"
    assert body["answer"] == "X is Y."
    assert body["model_used"] == "mock-model"
    assert body["chunks"] is None


def test_list_rag_interactions_with_chunks(client: TestClient) -> None:
    chunk = MagicMock()
    chunk.chunk_id = uuid.uuid4()
    chunk.document_id = uuid.uuid4()
    chunk.score = 0.85

    log_with_chunks = RagInteractionLog(
        id=uuid.uuid4(),
        conversation_id=uuid.uuid4(),
        question="q",
        answer="a",
        model_used="mock-model",
        chunks=[chunk],
        prompt_tokens=None,
        completion_tokens=None,
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    mock_uc = MagicMock()
    mock_uc.handle.return_value = [log_with_chunks]

    with patch(
        "app.container.support.SupportContainer.export_rag_interactions",
        return_value=mock_uc,
    ):
        response = client.get("/analytics/rag-interactions")

    body = response.json()[0]
    assert body["chunks"] is not None
    assert len(body["chunks"]) == 1
    assert "score" in body["chunks"][0]
