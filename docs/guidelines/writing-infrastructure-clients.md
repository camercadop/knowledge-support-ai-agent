# Writing Infrastructure Clients

This document describes how to implement an infrastructure client in this project.

## Purpose

Infrastructure clients live in `app/infrastructure/` and wrap external SDKs or services (LLM APIs, messaging platforms, vector databases, etc.). They expose a clean, typed interface to the application layer.

## Structure

```python
from app.config.settings import settings

_client = ExternalSDK(api_key=settings.external_api_key)


class ExternalResponse:
    """Holds the typed result of an external API call."""

    def __init__(self, content: str) -> None:
        """Initialize with the response content."""
        self.content = content


def call(payload: str) -> ExternalResponse:
    """Send a request to the external service and return the typed result.

    Expects a plain string payload and wraps the SDK response.
    """
    raw = _client.some_method(payload)
    return ExternalResponse(content=raw.text)
```

## Rules

- One module per external integration, under `app/infrastructure/<integration>/`.
- Every infrastructure client that the application layer depends on must implement a port defined in `app/application/ports/` — the application layer must never import the concrete client directly.
- Instantiate the SDK client at module level using settings.
- Wrap SDK responses in a typed dataclass or class — never return raw SDK objects to the application layer.
- Infrastructure clients must not import from `app/application/` except for the port they implement.
- All public functions must have docstrings describing what they expect and what they return.
