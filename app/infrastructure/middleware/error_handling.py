import json
import logging
import traceback
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException
from starlette.types import ASGIApp, Receive, Scope, Send

from app.config.settings import settings
from app.infrastructure.security.logger import log_security_event

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware:
    """ASGI middleware that catches unhandled exceptions and
    returns safe error responses.

    In production, no stack traces or internal details are exposed to clients.
    Full error details are logged server-side for debugging.
    HTTPException and RequestValidationError are handled via add_exception_handler
    and are not caught here.
    """

    def __init__(self, app: ASGIApp, *, enabled: bool) -> None:
        self.app = app
        self.enabled = enabled

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if not self.enabled or scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        try:
            await self.app(scope, receive, send)
        except Exception:
            logger.error("Unhandled exception: %s", traceback.format_exc())
            await self._respond(
                send,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                {"error": "Internal server error"},
            )

    async def _respond(
        self, send: Send, status_code: int, body: dict[str, Any]
    ) -> None:
        """Send a JSON error response directly via the ASGI send callable."""
        response_body = json.dumps(body).encode("utf-8")
        await send(
            {
                "type": "http.response.start",
                "status": status_code,
                "headers": [
                    (b"content-type", b"application/json"),
                ],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": response_body,
            }
        )


def setup_error_handlers(app: FastAPI) -> FastAPI:
    """Attach error handling middleware and exception handlers to the ASGI app.

    Registers:
    - ErrorHandlingMiddleware for unhandled Exception (500).
    - exception_handler for HTTPException (status code from exception).
    - exception_handler for RequestValidationError (422).

    Args:
        app: The FastAPI application.

    Returns:
        The app with error handling registered.
    """
    if not settings.error_handling_enabled:
        return app

    app.add_middleware(ErrorHandlingMiddleware, enabled=True)

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exception_handler(
        request: Request, exc: RateLimitExceeded
    ) -> JSONResponse:
        limit = getattr(exc, "limit", None)
        limit_str = str(limit) if limit is not None else "unknown"
        log_security_event(
            "http.rate_limit_exceeded",
            path=request.url.path,
            ip=request.client.host if request.client else "unknown",
            limit=limit_str,
            reason=exc.detail,
        )
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"error": exc.detail},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        logger.error("Unhandled exception: %s", traceback.format_exc())
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.error("Unhandled exception: %s", traceback.format_exc())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"error": "Invalid request data"},
        )

    return app
