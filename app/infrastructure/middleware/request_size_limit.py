import logging

from fastapi import FastAPI
from starlette.types import ASGIApp, Receive, Scope, Send

from app.config.settings import settings

logger = logging.getLogger(__name__)


class RequestSizeLimitMiddleware:
    """ASGI middleware that rejects requests exceeding a configurable body size.

    Checks the ``Content-Length`` header of incoming requests against a
    global limit. Requests without a ``Content-Length`` header (e.g.
    chunked transfer) are allowed through. Rejected requests receive a
    ``413 Payload Too Large`` response.
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        limit: int,
        enabled: bool,
    ) -> None:
        self.app = app
        self.limit = limit
        self.enabled = enabled

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if not self.enabled or scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        content_length = self._get_content_length(scope)
        if content_length is not None and content_length > self.limit:
            logger.warning(
                "Request body size %d bytes exceeds limit of %d bytes",
                content_length,
                self.limit,
            )
            await self._reject(send)
            return

        await self.app(scope, receive, send)

    def _get_content_length(self, scope: Scope) -> int | None:
        headers: list[tuple[bytes, bytes]] = scope.get("headers", [])
        for name, value in headers:
            if name == b"content-length":
                try:
                    return int(value)
                except ValueError:
                    return None
        return None

    async def _reject(self, send: Send) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": 413,
                "headers": [
                    (b"content-type", b"application/json"),
                ],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": b'{"error": "request body too large"}',
            }
        )


def setup_request_size_limiter(app: FastAPI) -> FastAPI:
    """Attach the request size limit middleware to the ASGI app.

    Args:
        app: The ASGI application.

    Returns:
        The app with the request size limit middleware registered.
    """
    app.add_middleware(
        RequestSizeLimitMiddleware,
        limit=settings.request_size_limit_default,
        enabled=settings.request_size_limit_enabled,
    )
    return app
