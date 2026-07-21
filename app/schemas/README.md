# schemas

This package contains the Pydantic models that define the API contract. Schemas are used exclusively for request validation and response serialization at the HTTP boundary. They are never passed to the ORM layer or used as internal data structures inside services.

## Chat

| Schema | Direction | Fields |
|--------|-----------|--------|
| `ChatRequest` | inbound | `phone: str`, `message: str` |
| `ChatResponse` | outbound | `reply: str` |

## Documents

| Schema | Direction | Fields |
|--------|-----------|--------|
| `DocumentIngestRequest` | inbound | `title: str`, `source: str \| None`, `content: str` |
| `DocumentIngestResponse` | outbound | `id: UUID`, `title: str`, `source: str \| None` |

## Modules

- `chat.py` — `ChatRequest` and `ChatResponse`
- `documents.py` — `DocumentIngestRequest` and `DocumentIngestResponse`
