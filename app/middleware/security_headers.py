from collections.abc import Callable
from typing import Any

from starlette.types import ASGIApp, Message, Receive, Scope, Send


class SecurityHeadersMiddleware:
    """ASGI middleware that sets security headers on all HTTP responses."""

    def __init__(
        self,
        app: ASGIApp,
        *,
        enabled: bool,
        content_security_policy: str,
        x_content_type_options: str,
        x_frame_options: str,
        strict_transport_security: str,
        referrer_policy: str,
    ) -> None:
        self.app = app
        self.enabled = enabled
        self._headers: dict[str, str] = {
            "content-security-policy": content_security_policy,
            "x-content-type-options": x_content_type_options,
            "x-frame-options": x_frame_options,
            "strict-transport-security": strict_transport_security,
            "referrer-policy": referrer_policy,
        }

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if not self.enabled or scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        wrapped_send: Callable[[Message], Any] = self._wrap_send(send)
        await self.app(scope, receive, wrapped_send)

    def _wrap_send(self, send: Send) -> Callable[[Message], Any]:
        async def wrapped_send(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers: list[tuple[bytes, bytes]] = list(message.get("headers", []))
                for name, value in self._headers.items():
                    headers.append((name.encode("latin-1"), value.encode("latin-1")))
                message["headers"] = headers
            await send(message)

        return wrapped_send
