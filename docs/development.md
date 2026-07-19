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
uv run uvicorn app.main:app --reload
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `OPENAI_API_KEY` | OpenAI API key |
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
    core/         # Shared utilities and base classes
    config/       # Settings and environment configuration
    domain/       # Domain models and business logic
    application/  # Use cases and orchestration
    infrastructure/  # Database, LLM, WhatsApp, vector store
    repositories/ # Data access layer
    models/       # SQLAlchemy models
    schemas/      # Pydantic schemas

tests/
docs/
    adr/          # Architecture Decision Records
```

## Decision Tracking

Architectural decisions are tracked in two places:

- `docs/adr/` - formal, accepted, and binding decisions


Always consult both before implementing a new feature.
