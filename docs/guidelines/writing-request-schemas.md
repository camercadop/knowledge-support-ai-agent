# Writing Request Schemas

This document describes how to define Pydantic schemas for API request and response contracts in this project.

## Purpose

Schemas live in `app/schemas/` and are the only types that cross the API boundary. They must never import from `app/models/`.

## Structure

```python
from pydantic import BaseModel


class MyResourceRequest(BaseModel):
    """Payload for creating a my-resource."""

    field: str


class MyResourceResponse(BaseModel):
    """Response returned after processing a my-resource request."""

    id: str
    field: str
```

## Rules

- One file per domain, named after the domain (e.g. `chat.py`, `contact.py`).
- Request schemas use the `Request` suffix; response schemas use the `Response` suffix.
- Schemas must not import from `app/models/` — they are independent of the ORM layer.
- All fields must have type annotations.
- Every schema class must have a docstring describing its contract.
