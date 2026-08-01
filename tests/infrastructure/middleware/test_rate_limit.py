from collections.abc import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.infrastructure.middleware.rate_limit import MovingWindowRateLimitMiddleware


def _make_app(default_limit: str = "1/minute", enabled: bool = True) -> FastAPI:
    app = FastAPI()
    limiter = Limiter(
        key_func=get_remote_address,
        strategy="moving-window",
        default_limits=[default_limit],
        enabled=True,
    )
    app.state.limiter = limiter
    app.add_middleware(MovingWindowRateLimitMiddleware)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


@pytest.fixture()
def client() -> Generator[TestClient]:
    yield TestClient(_make_app())


def test_rate_limit_allows_request_within_limit(client: TestClient) -> None:
    """A request within the rate limit returns a successful response."""
    response = client.get("/health")
    assert response.status_code == 200


def test_rate_limit_returns_429_when_exceeded() -> None:
    """Requests exceeding the limit return 429 Too Many Requests."""
    test_app = _make_app(default_limit="1/minute")
    test_client = TestClient(test_app)

    response = test_client.get("/health")
    assert response.status_code == 200

    response = test_client.get("/health")
    assert response.status_code == 429


def test_rate_limit_returns_429_with_detail() -> None:
    """A 429 response includes an error message."""
    test_app = _make_app(default_limit="1/minute")
    test_client = TestClient(test_app)

    test_client.get("/health")
    response = test_client.get("/health")
    assert response.status_code == 429
    assert "error" in response.json()


def test_rate_limiting_disabled_when_setting_false() -> None:
    """When rate limiting is disabled, no 429 responses are returned."""
    test_app = FastAPI()
    limiter = Limiter(
        key_func=get_remote_address,
        strategy="moving-window",
        default_limits=["1/minute"],
        enabled=False,
    )
    test_app.state.limiter = limiter
    test_app.add_middleware(MovingWindowRateLimitMiddleware)

    @test_app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    test_client = TestClient(test_app)

    for _ in range(100):
        response = test_client.get("/health")
        assert response.status_code == 200