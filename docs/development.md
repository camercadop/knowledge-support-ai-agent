# Development Guide

## Requirements

- Python 3.13+
- Docker & Docker Compose
- uv

## Local Setup

```bash
cp .env.example .env
# Fill in your values

uv sync
docker compose up -d
uv run alembic upgrade head
```

## Running

```bash
uv run uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`.

## Trying it out

Send a chat message:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890", "message": "Hello, what can you help me with?"}'
```

Ingest a document:

```bash
curl -X POST http://localhost:8000/documents \
  -H "Content-Type: application/json" \
  -d '{"title": "My Doc", "source": "manual", "content": "Your document text here..."}'
```

Or use the interactive docs at `http://localhost:8000/docs`.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `CHAT_PROVIDER` | Chat provider: `openai`, `ollama`, `openrouter`, `mock` |
| `CHAT_API_KEY` | API key for the chat provider |
| `CHAT_MODEL` | Model name (e.g. `gpt-4o-mini`) |
| `CHAT_BASE_URL` | Optional base URL override for the chat provider |
| `EMBEDDING_PROVIDER` | Embedding provider: `openai`, `ollama`, `mock` |
| `EMBEDDING_API_KEY` | API key for the embedding provider |
| `EMBEDDING_MODEL` | Embedding model name (default: `text-embedding-3-small`) |
| `EMBEDDING_DIMENSIONS` | Embedding vector dimensions (default: `1536`) |
| `EMBEDDING_BASE_URL` | Optional base URL override for the embedding provider |
| `WHATSAPP_TOKEN` | WhatsApp Cloud API token |
| `WHATSAPP_VERIFY_TOKEN` | Webhook verification token |

## Running Tests

```bash
uv run pytest
```

## Linting & Type Checking

```bash
uv run ruff check .
uv run mypy app/
```

## Conventions

### Code Style

- Follow existing project patterns — do not refactor unless explicitly asked.
- All new classes and methods must have Google-style docstrings.
- All function parameters must have type annotations.
- Use `X | None` instead of `Optional[X]`.
- Do not use `from __future__ import annotations`.

### Logging

- Declare a module-level logger: `logger = logging.getLogger(__name__)`
- Use `%s`-style formatting — never f-strings in log calls.
- Never log passwords, tokens, secrets, or full request bodies.

### Database

- All models define their own UUID primary key explicitly.
- Each model field must have a comment explaining its purpose.

## Project Structure

```
app/
    api/          # Route handlers
    application/  # Use cases and ports
        models/   # Application-layer value objects
        ports/    # Interfaces for infrastructure dependencies
            repositories/  # One abstract repo per aggregate root
            unit_of_work/  # Domain-scoped transactional boundaries
    config/       # Settings and environment configuration
    domain/       # Domain models and business logic
    infrastructure/
        ai/           # Chat and embedding provider implementations
        database/     # Models, repositories, and migrations
        vectorstores/ # Vector store implementations (pgvector)
        whatsapp/     # WhatsApp Cloud API integration
    schemas/      # Pydantic schemas

docs/
    adr/          # Architecture Decision Records
```

## Request Flows

### POST /chat

```mermaid
sequenceDiagram
    participant Client
    participant Router as chat.py (API)
    participant UC as AnswerQuestion
    participant UoW as SqlAlchemyMessagingUnitOfWork
    participant DB as PostgreSQL
    participant LLM as OpenAIChatModel
    participant OpenAI as OpenAI API

    Client->>Router: POST /chat {phone, message}
    Router->>UC: handle(phone, message)
    UC->>UoW: contacts.get_or_create_by_phone(phone)
    UoW->>DB: SELECT / INSERT contact
    UC->>UoW: conversations.get_or_create_for_contact(contact_id)
    UoW->>DB: SELECT / INSERT conversation
    UC->>UoW: messages.list_by_conversation(conversation_id)
    UoW->>DB: SELECT messages
    UC->>LLM: generate(history + user_message)
    LLM->>OpenAI: responses.create(model, input)
    OpenAI-->>LLM: output_text, token usage
    LLM-->>UC: ChatResponse
    UC->>UoW: messages.create(conversation_id, "user", ...)
    UC->>UoW: messages.create(conversation_id, "assistant", ...)
    UC->>UoW: commit()
    UoW->>DB: COMMIT
    UC-->>Router: reply text
    Router-->>Client: {reply}
```

### POST /documents

```mermaid
sequenceDiagram
    participant Client
    participant Router as documents.py (API)
    participant UC as IngestDocument
    participant UoW as SqlAlchemyKnowledgeUnitOfWork
    participant DB as PostgreSQL
    participant Embed as OpenAIEmbeddingModel
    participant VS as PgVectorStore
    participant OpenAI as OpenAI API

    Client->>Router: POST /documents {title, source, content}
    Router->>UC: handle(title, source, content)
    UC->>UoW: documents.create(...)
    UoW->>DB: INSERT document
    loop for each chunk
        UC->>Embed: embed(chunk)
        Embed->>OpenAI: embeddings.create(...)
        OpenAI-->>Embed: vector
        UC->>UoW: document_chunks.create(...)
        UoW->>DB: INSERT document_chunk
        UC->>VS: upsert(chunk_id, ...)
    end
    UC->>UoW: commit()
    UoW->>DB: COMMIT
    UC-->>Router: Document
    Router-->>Client: {id, title, source}
```

## Decision Tracking

Architectural decisions are tracked in `docs/adr/` — formal, accepted, and binding decisions.

Always consult before implementing a new feature.
