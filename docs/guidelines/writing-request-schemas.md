# Writing Request Schemas

This document describes how to define Pydantic schemas for API request and response contracts in this project.

## Purpose

Schemas live in `app/schemas/` and are the only types that cross the API boundary. They must never import from `app/models/`.

## Structure

```python
from pydantic import BaseModel, Field, field_validator


class MyResourceRequest(BaseModel):
    """Payload for creating a my-resource."""

    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: str) -> str:
        """Strip newline characters to prevent log injection."""
        return v.replace("\n", " ").replace("\r", " ")


class MyResourceResponse(BaseModel):
    """Response returned after processing a my-resource request."""

    id: str
    field: str
```

## Rules

- One file per domain, named after the domain (e.g. `chat.py`, `contact.py`).
- Request schemas use the `Request` suffix; response schemas use the `Response` suffix.
- Schemas must not import from `app/infrastructure/database/models/` — they are independent of the ORM layer.
- All fields must have type annotations.
- Every schema class must have a docstring describing its contract.
- All validation and sanitization must live in the schema — never in the route handler.
- Use `Field(min_length=..., max_length=...)` for length constraints on string fields.
- Use `@field_validator` for sanitization logic.
- Route handlers must use schema fields directly without re-validating or re-sanitizing them.
