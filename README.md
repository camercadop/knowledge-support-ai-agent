# Knowledge Support AI Agent

A conversational AI platform built with FastAPI that demonstrates RAG, semantic memory, tool calling, and a layered backend architecture. WhatsApp Cloud API is used as the communication channel.

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
```

## Running

```bash
uv run uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`.

## Testing

```bash
uv run pytest
```

## Linting & Type Checking

```bash
uv run ruff check .
uv run mypy app/
```

## License

MIT
