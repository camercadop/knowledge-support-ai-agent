from collections.abc import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.infrastructure.middleware.request_size_limit import RequestSizeLimitMiddleware


def _make_app(limit: int = 1_048_576, enabled: bool = True) -> FastAPI:
    app = FastAPI()
    app.add_middleware(RequestSizeLimitMiddleware, limit=limit, enabled=enabled)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


@pytest.fixture()
def client() -> Generator[TestClient]:
    yield TestClient(_make_app())


def test_request_size_limit_allows_request_within_limit(client: TestClient) -> None:
    """A request within the size limit returns a successful response."""
    response = client.get("/health")
    assert response.status_code == 200


def test_request_size_limit_returns_413_when_exceeded() -> None:
    """A request exceeding the size limit returns 413 Payload Too Large."""
    test_app = _make_app(limit=10)
    test_client = TestClient(test_app)

    response = test_client.get(
        "/health",
        headers={"Content-Length": "100"},
    )
    assert response.status_code == 413


def test_request_size_limit_returns_413_with_error_body() -> None:
    """A 413 response includes an error message."""
    test_app = _make_app(limit=10)
    test_client = TestClient(test_app)

    response = test_client.get(
        "/health",
        headers={"Content-Length": "100"},
    )
    assert response.status_code == 413
    assert "error" in response.json()


def test_request_size_limit_allows_request_without_content_length() -> None:
    """A request without a Content-Length header is allowed through."""
    test_app = _make_app(limit=10)
    test_client = TestClient(test_app)

    response = test_client.get("/health")
    assert response.status_code == 200


def test_request_size_limit_disabled_allows_all_requests() -> None:
    """When the middleware is disabled, requests exceeding the limit pass through."""
    test_app = _make_app(limit=10, enabled=False)
    test_client = TestClient(test_app)

    response = test_client.get(
        "/health",
        headers={"Content-Length": "100"},
    )
    assert response.status_code == 200