# Knowledge Support AI Agent

[![CI](https://github.com/camercadop/knowledge-support-ai-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/camercadop/knowledge-support-ai-agent/actions/workflows/ci.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-grade reference implementation of a conversational AI support agent. Built to demonstrate how to structure a real-world AI backend using Clean Architecture — with RAG, semantic memory, persistent chat history, and provider independence baked in from the start.

The goal is to show that AI-powered applications don't have to be prototype spaghetti: business logic stays isolated from LLM providers, databases, and messaging platforms, making every layer independently testable and replaceable.

WhatsApp Cloud API is the intended communication channel, with a REST API available for direct integration and local development.

## Features

- Conversational chat with persistent history per contact
- RAG — knowledge chunks retrieved via semantic search on every turn
- Document ingestion — chunking, embedding, and pgvector indexing
- Tool calling — `search_documents` and `get_current_date` built in
- Provider independence — chat and embedding providers are swappable at config time
- WhatsApp Cloud API webhook integration
- REST API and CLI interfaces

## Architecture

```mermaid
flowchart TB
    user["User"]
    whatsapp["WhatsApp\n[External]"]
    openai["OpenAI\n[External]"]

    subgraph agent["Knowledge Support AI Agent"]
        api["API Layer\nFastAPI"]
        cli["CLI\nTyper"]
        app["Application Layer\nUse cases & ports"]
        infra["Infrastructure\nDB · LLM · Vector store · Tools"]
        db["PostgreSQL + pgvector"]
    end

    user -->|"POST /chat"| api
    user -->|"agent chat / ingest"| cli
    whatsapp -->|"Webhook"| api
    api --> app
    cli --> app
    app --> infra
    infra -->|"Chat & Embeddings"| openai
    infra -->|"Reads / writes"| db
```

> See [Architecture](docs/architecture.md) for C4 Level 0–2 diagrams.

## Stack

- Python 3.13+, FastAPI, Typer, SQLAlchemy, Alembic
- PostgreSQL, pgvector
- OpenAI Responses API
- Docker, Docker Compose
- uv, Pytest, Ruff, MyPy, import-linter

## Prerequisites

- [Python 3.13+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Docker & Docker Compose](https://docs.docker.com/get-docker/)
- An OpenAI API key

## Setup

```bash
git clone <repo-url>
cd knowledge-support-ai-agent

cp .env.example .env
# Fill in your values in .env

uv sync
docker compose up -d
uv run alembic upgrade head
```

## Configuration

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
| `LOG_LEVEL` | Log level: `DEBUG`, `INFO`, `WARNING` (default: `INFO`) |
| `LOG_FORMAT` | Log format: `text` for console, `json` for production (default: `text`) |

## Running

### API

```bash
uv run uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`.

### CLI

```bash
uv run agent --help
```

## Trying it out

### Via API

Send a chat message:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890", "message": "Hello, what can you help me with?"}'
```

Ingest a document into the knowledge base:

```bash
curl -X POST http://localhost:8000/documents \
  -H "Content-Type: application/json" \
  -d '{"title": "My Doc", "source": "manual", "content": "Your document text here..."}'
```

Or use the interactive docs at `http://localhost:8000/docs`.

### Via CLI

Start an interactive chat session:

```bash
uv run agent chat --phone "+1234567890"
```

Ingest a document from a file:

```bash
uv run agent ingest --file ./doc.txt --title "My Doc"
```

Clear a contact's chat history:

```bash
uv run agent clear-history --phone "+1234567890"
```

## Project Structure

```
app/
    api/              # Route handlers
    application/      # Use cases and orchestration
        models/       # Application-layer value objects
        ports/        # Abstract interfaces (ports)
            repositories/  # One abstract repo per aggregate root
            unit_of_work/  # Domain-scoped transactional boundaries
    cli/              # Typer CLI entry point
        commands/     # One module per command group
        context.py    # Request context manager (container + session lifecycle)
    config/           # Settings and logging configuration
    container/        # Composition Root — ApplicationContainer composes domain-scoped containers
    domain/           # Domain models and business logic
    infrastructure/
        ai/           # Chat and embedding provider implementations
            prompt_builder/ # PromptBuilder implementations
            tools/    # Tool registry, @tool decorator, and tool implementations
        database/
            sqlalchemy/ # Models, repositories, migrations, and PostgreSQL engine
            sqlite/     # In-memory SQLite engine for tests
        vectorstores/ # Vector store implementations (pgvector)
        whatsapp/     # WhatsApp Cloud API integration
    schemas/          # Pydantic schemas

tests/
    api/              # mirrors app/api/
    application/      # mirrors app/application/
    infrastructure/   # mirrors app/infrastructure/
    conftest.py       # shared fixtures
```

## Testing

```bash
uv run pytest
```

## Linting & Type Checking

```bash
uv run ruff check .
uv run mypy app/
uv run lint-imports
```

## Dependency Audit

```bash
uv audit --preview-features audit-command
```

## Documentation

- [Architecture](docs/architecture.md) — C4 diagrams (context, container, component) and request flow sequences
- [Development Guide](docs/development.md) — conventions, local setup, testing, linting, and code style rules
- [Data Model](docs/data-model.md) — database conventions, base model fields, and migration rules
- [Architecture Decision Records](docs/adr/) — formal, binding decisions that shaped the system design
- [Guidelines](docs/guidelines/) — how-to references for implementing common patterns correctly
- [Contributing](CONTRIBUTING.md) — branching, commit conventions, and PR process

## License

MIT
