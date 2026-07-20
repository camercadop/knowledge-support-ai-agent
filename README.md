# Knowledge Support AI Agent

A conversational AI platform built with FastAPI that demonstrates RAG, semantic memory, tool calling, and Clean Architecture. WhatsApp Cloud API is used as the communication channel.

## Stack

- Python 3.13+, FastAPI, SQLAlchemy, Alembic
- PostgreSQL, pgvector
- OpenAI Responses API
- Docker, Docker Compose
- uv, Pytest, Ruff, MyPy

## Setup

```bash
cp .env.example .env
# Fill in your values in .env

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

Once the server is running, send a chat message:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890", "message": "Hello, what can you help me with?"}'
```

Or use the interactive docs at `http://localhost:8000/docs`.

## Testing

```bash
uv run pytest
```

## Linting & Type Checking

```bash
uv run ruff check .
uv run mypy app/
```

## Documentation

- [Architecture](docs/architecture.md)
- [Development Guide](docs/development.md)
- [Data Model](docs/data-model.md)
- [Architecture Decision Records](docs/adr/)

## License

MIT
