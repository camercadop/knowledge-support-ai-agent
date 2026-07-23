# schemas

This package contains the Pydantic models that define the API contract. Schemas are used exclusively for request validation and response serialization at the HTTP boundary. They are never passed to the ORM layer or used as internal data structures inside services.

## Chat

| Schema | Direction | Fields |
|--------|-----------|--------|
| `ChatRequest` | inbound | `phone: str`, `message: str` |
| `ChunkReference` | outbound | `chunk_id: UUID`, `document_id: UUID`, `score: float` |
| `ChatResponse` | outbound | `reply: str`, `chunks: list[ChunkReference] \| None` |

## Documents

| Schema | Direction | Fields |
|--------|-----------|--------|
| `DocumentIngestRequest` | inbound | `title: str`, `source: str \| None`, `content: str` |
| `DocumentIngestResponse` | outbound | `id: UUID`, `title: str`, `source: str \| None` |

## Modules

- `chat.py` — `ChatRequest`, `ChunkReference`, and `ChatResponse`
- `documents.py` — `DocumentIngestRequest` and `DocumentIngestResponse`
