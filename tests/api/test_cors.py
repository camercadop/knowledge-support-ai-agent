from collections.abc import Generator

import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from app.config.settings import Settings
from app.main import app


@pytest.fixture()
def client() -> Generator[TestClient]:
    yield TestClient(app)


def test_cors_denies_cross_origin_by_default(client: TestClient) -> None:
    """A cross-origin request with no allowed origins returns no CORS headers."""
    response = client.get(
        "/health",
        headers={"Origin": "http://evil.com"},
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_cors_allows_same_origin(client: TestClient) -> None:
    """A same-origin request is not affected by CORS middleware."""
    response = client.get(
        "/health",
        headers={"Origin": "http://localhost:8000"},
    )
    assert response.status_code == 200


def test_cors_preflight_denied_by_default(client: TestClient) -> None:
    """A preflight request from a non-allowed origin is denied."""
    response = client.options(
        "/chat",
        headers={
            "Origin": "http://evil.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert "access-control-allow-origin" not in response.headers


def test_cors_allows_configured_origins() -> None:
    """When cors_origins is configured, matching origins receive CORS headers."""
    test_app = FastAPI()
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
        allow_credentials=False,
    )

    @test_app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(test_app)
    response = client.get(
        "/health",
        headers={"Origin": "http://localhost:3000"},
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_cors_denies_non_configured_origins() -> None:
    """When cors_origins is configured, non-matching origins are denied."""
    test_app = FastAPI()
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
        allow_credentials=False,
    )

    @test_app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(test_app)
    response = client.get(
        "/health",
        headers={"Origin": "http://evil.com"},
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers