# database

This sub-package organizes database backends by ORM/driver. Each backend lives in its own subdirectory and is fully self-contained.

## Structure

```
database/
    sqlalchemy/
        migrations/       # Alembic migrations (ORM-specific, shared across backends)
        postgresql/       # PostgreSQL backend
            models/
            repositories/
            unit_of_work/
            base.py       # Declarative base with id, created_at, updated_at
            engine.py     # PostgreSQL engine, SessionLocal, and get_db dependency
        sqlite/           # SQLite backend
            engine.py     # In-memory SQLite engine and get_db dependency for tests
```

## sqlalchemy/postgresql/repositories

All concrete repositories extend `SqlAlchemyRepository[OrmT, DomainT]` from `repositories/base.py`. The base class provides session wiring, UUID generation, and default implementations of `get_by_id`, `list`, `update`, and `delete`. Subclasses declare `_orm_class` once and implement `_to_domain` to map ORM rows to domain models.

`get_db` is a FastAPI dependency that opens a session, yields it to the handler, and closes it when the request is done regardless of outcome.

```mermaid
flowchart
    FastAPI -->|Depends| get_db
    get_db -->|yields| Session
    Session --> PostgreSQL
```

## sqlalchemy/sqlite

Provides an in-memory SQLite session factory that reuses the same SQLAlchemy models and `Base.metadata`. Intended for tests only — not suitable for production.

```mermaid
flowchart
    Tests -->|Depends| get_db
    get_db -->|yields| Session
    Session --> SQLiteInMemory
```
