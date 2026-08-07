# Writing Infrastructure Clients

This document describes how to implement an infrastructure client in this project.

## Purpose

Infrastructure clients live in `app/infrastructure/` and wrap external SDKs or services (LLM APIs, messaging platforms, vector databases, etc.). They expose a clean, typed interface to the application layer.

## Structure

Infrastructure clients implement a port defined in `app/application/<domain>/ports/`. They receive their dependencies via constructor injection — never by reading settings or instantiating SDKs at module level.

```python
from dataclasses import dataclass

from app.application.<domain>.ports.my_port import MyPort


@dataclass(frozen=True)
class ExternalServiceSettings:
    """Configuration options for ExternalServiceClient."""

    api_key: str
    base_url: str | None = None


class ExternalServiceClient(MyPort):
    """MyPort implementation backed by ExternalService."""

    def __init__(self, settings: ExternalServiceSettings) -> None:
        """Initialize the SDK client from the provided settings.

        Args:
            settings: Configuration options for the external service.
        """
        self._client = ExternalSDK(
            api_key=settings.api_key,
            base_url=settings.base_url,
        )
        self._settings = settings

    def do_something(self, payload: str) -> MyResult:
        """Send a request to the external service and return the typed result.

        Args:
            payload: The input to send.

        Returns:
            A typed result wrapping the SDK response.
        """
        raw = self._client.some_method(payload)
        return MyResult(content=raw.text)
```

The settings dataclass is constructed in the domain container's `_setup` method from the global `settings` object and injected into the client. Route handlers never import or instantiate infrastructure clients directly.

## Rules

- One module per external integration, under `app/infrastructure/<integration>/`.
- Every infrastructure client that the application layer depends on must implement a port defined in `app/application/<domain>/ports/` — the application layer must never import the concrete client directly.
- Receive SDK configuration via constructor injection from settings — never read settings at module level outside of `__init__`.
- Wrap SDK responses in a typed dataclass or class — never return raw SDK objects to the application layer.
- Infrastructure clients must not import from `app/application/` except for the port they implement.
- All public methods must have docstrings describing what they expect and what they return.
