# schemas

This package contains the Pydantic models that define the API contract. Schemas are used exclusively for request validation and response serialization at the HTTP boundary. They are never passed to the ORM layer or used as internal data structures inside services.

## Chat

| Schema | Direction | Fields |
|--------|-----------|--------|
| `ChatRequest` | inbound | `phone: str` (E.164, max 15 chars), `message: str` (min 1, max 4096 chars) |
| `ChunkReference` | outbound | `chunk_id: UUID`, `document_id: UUID`, `score: float`, `document_title: str`, `source: str | None` |
| `ChatResponse` | outbound | `reply: str`, `chunks: list[ChunkReference] \| None` |

### Validation rules

- `phone` — must match E.164 format (`+` followed by 1–15 digits). Newline characters are stripped before format validation to prevent log injection.
- `message` — length bounds only. Prompt injection sanitization is applied in the application layer via `MessageSanitizer` before the message enters the prompt pipeline.

## Documents

| Schema | Direction | Fields |
|--------|-----------|--------|
| `DocumentIngestRequest` | inbound | `title: str`, `source: str \| None`, `content: str` (max 100,000 chars) |
| `DocumentIngestResponse` | outbound | `id: UUID`, `title: str`, `source: str \| None` |

## Modules

- `chat.py` — `ChatRequest`, `ChunkReference`, and `ChatResponse`
- `documents.py` — `DocumentIngestRequest` and `DocumentIngestResponse`
