from collections.abc import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config.settings import Settings
from app.main import app
from app.middleware.security_headers import SecurityHeadersMiddleware


@pytest.fixture()
def client() -> Generator[TestClient]:
    yield TestClient(app)


def test_security_headers_present_on_response(client: TestClient) -> None:
    """All security headers are present on responses when enabled."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "content-security-policy" in response.headers
    assert "x-content-type-options" in response.headers
    assert "x-frame-options" in response.headers
    assert "strict-transport-security" in response.headers
    assert "referrer-policy" in response.headers


def test_security_headers_values_match_defaults(client: TestClient) -> None:
    """Security header values match the configured defaults."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["content-security-policy"] == (
        "default-src 'none'; frame-ancestors 'none'"
    )
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["strict-transport-security"] == (
        "max-age=31536000; includeSubDomains"
    )
    assert response.headers["referrer-policy"] == (
        "strict-origin-when-cross-origin"
    )


def test_security_headers_absent_when_disabled() -> None:
    """When security_headers_enabled is False, no security headers are set."""
    test_app = FastAPI()
    test_app.add_middleware(
        SecurityHeadersMiddleware,
        enabled=False,
        content_security_policy="default-src 'none'; frame-ancestors 'none'",
        x_content_type_options="nosniff",
        x_frame_options="DENY",
        strict_transport_security="max-age=31536000; includeSubDomains",
        referrer_policy="strict-origin-when-cross-origin",
    )

    @test_app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    client = TestClient(test_app)
    response = client.get("/health")
    assert response.status_code == 200
    assert "content-security-policy" not in response.headers
    assert "x-content-type-options" not in response.headers
    assert "x-frame-options" not in response.headers
    assert "strict-transport-security" not in response.headers
    assert "referrer-policy" not in response.headers