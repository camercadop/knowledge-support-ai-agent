# Layered Architecture

This document describes how to work within the project's layered architecture. For the architectural decision behind this structure, see [ADR-001](../adr/001-layered-architecture.md).

## Project Structure

The following is the default directory layout under `app/`. Each directory maps to a single layer with a well-defined responsibility.

```
app/
├── api/              # Route handlers
├── application/      # Use cases
│   ├── ports/        # Interfaces for infrastructure dependencies
│   └── <domain>/
│       └── <use_case>.py
├── config/           # Settings and configuration
├── domain/           # Domain models and business logic
├── infrastructure/   # External clients (DB engine, LLM, etc.)
│   ├── ai/
│   │   ├── chat/     # Chat completion provider implementations
│   │   ├── embeddings/ # Embedding provider implementations
│   │   └── mock/     # Mock implementations for testing
│   └── database/     # Models, repositories, and migrations
├── schemas/          # Pydantic request/response schemas
└── main.py
```

## Dependency Rule

Dependencies flow inward only. Outer layers may import from inner layers; inner layers must never import from outer layers.

```
api  →  application  →  infrastructure
```

## Where to Put New Code

### Adding a new endpoint

Create a route handler in `app/api/`. The handler must:

1. Parse and validate the request using a schema from `app/schemas/`.
2. Call the application layer to execute the use case.
3. Return the response.

```python
# app/api/my_resource.py
@router.post("/my-resource")
def create(payload: MySchema, db: Session = Depends(get_db)) -> MyResponseSchema:
    service = MyService(db)
    return service.create(payload)
```

### Adding a new use case

Create a use case class in `app/application/<domain>/`. The class must:

1. Coordinate repositories and infrastructure clients to fulfill the use case.
2. Call `db.commit()` once at the end — the use case owns the transaction boundary.

```python
# app/application/my_domain/do_something.py
class DoSomething:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = MyRepository(db)

    def handle(self, value: str) -> str:
        entity = self._repo.create(value)
        self._db.commit()
        return entity.field
```

### Adding a new database query

Add a method to the relevant repository in `app/infrastructure/database/repositories/`. See [Writing Repositories](writing-repositories.md) for the full implementation guide.

### Adding a new external integration

Create a client in `app/infrastructure/`. The application layer calls it; the infrastructure layer must not call back into the application layer.

## Adding a New Domain End-to-End

When adding a full new domain, follow these steps in order:

1. Create the model in `app/infrastructure/database/models/<domain>.py` — see [Writing Database Models](writing-database-models.md).
2. Generate and apply the migration: `uv run alembic revision --autogenerate -m "create <domain> table" && uv run alembic upgrade head`.
3. Create the repository in `app/infrastructure/database/repositories/<domain>.py` — see [Writing Repositories](writing-repositories.md).
4. Create the use case in `app/application/<domain>/<use_case>.py` — see [Writing Use Cases](writing-use-cases.md).
5. Create the schemas in `app/schemas/<domain>.py` — see [Writing Request Schemas](writing-request-schemas.md).
6. Create the endpoint in `app/api/<domain>.py`.
7. Register the router in `app/main.py`:

```python
from app.api.<domain> import router as <domain>_router

app.include_router(<domain>_router)
```

## What Not to Do

- Do not call `db.commit()` inside a repository — only the use case commits.
- Do not put query logic in `app/api/` or `app/application/` — all DB access goes through repositories.
- Do not import from `app/api/` or `app/application/` inside `app/infrastructure/`.
