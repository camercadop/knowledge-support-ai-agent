import logging
from collections.abc import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.exceptions import HTTPException
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_CONTENT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from app.infrastructure.middleware.error_handling import (
    ErrorHandlingMiddleware,
    setup_error_handlers,
)


def _make_app(*, use_setup: bool = True) -> FastAPI:
    app = FastAPI()

    @app.get("/raise")
    def raise_error() -> None:
        raise RuntimeError("something went wrong")

    @app.get("/http-error")
    def raise_http_error() -> None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="not found")

    @app.get("/validation-error")
    def raise_validation_error(q: int) -> dict[str, int]:
        return {"q": q}

    if use_setup:
        setup_error_handlers(app)

    return app


@pytest.fixture()
def client() -> Generator[TestClient]:
    yield TestClient(_make_app())


def test_generic_exception_returns_500_with_safe_message(client: TestClient) -> None:
    """An unhandled exception returns 500 with no internal details."""
    response = client.get("/raise")
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"error": "Internal server error"}


def test_generic_exception_does_not_expose_stack_trace(client: TestClient) -> None:
    """A 500 response does not contain a stack trace."""
    body = client.get("/raise").json()
    assert "traceback" not in body
    assert "RuntimeError" not in body


def test_error_handling_disabled_allows_exception_to_propagate() -> None:
    """When the middleware is disabled, exceptions propagate normally."""
    app = FastAPI()
    app.add_middleware(ErrorHandlingMiddleware, enabled=False)

    @app.get("/raise")
    def raise_error() -> None:
        raise RuntimeError("something went wrong")

    with pytest.raises(RuntimeError):
        TestClient(app).get("/raise")


def test_generic_exception_logs_error(caplog: pytest.LogCaptureFixture) -> None:
    """An unhandled exception is logged as an error."""
    test_client = TestClient(_make_app())
    with caplog.at_level(logging.ERROR):
        test_client.get("/raise")

    assert any("Unhandled exception" in record.getMessage() for record in caplog.records)


def test_http_exception_returns_correct_status_and_detail(client: TestClient) -> None:
    """An HTTPException returns the exception's status code and detail."""
    response = client.get("/http-error")
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json() == {"error": "not found"}


def test_request_validation_error_returns_422(client: TestClient) -> None:
    """A RequestValidationError returns 422 with a safe message."""
    response = client.get("/validation-error", params={"q": "not-an-int"})
    assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT
    assert response.json() == {"error": "Invalid request data"}
