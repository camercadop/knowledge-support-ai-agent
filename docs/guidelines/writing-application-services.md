# Writing Application Services

This document describes how to implement an application service in this project.

## Purpose

Services live in `app/application/<domain>/service.py` and orchestrate repositories and infrastructure clients to fulfill a use case. They own the transaction boundary.

## Structure

```python
from sqlalchemy.orm import Session

from app.repositories.my_model import MyModelRepository


class MyDomainService:
    """Orchestrates use cases for the my-domain domain."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self._db = db
        self._repo = MyModelRepository(db)

    def do_something(self, value: str) -> str:
        """Execute the use case and return the result.

        Persists the entity and commits the transaction.
        """
        entity = self._repo.create(value)
        self._db.commit()
        return entity.field
```

## Rules

- One service class per domain, in `app/application/<domain>/service.py`.
- The constructor receives a `Session` and instantiates all required repositories.
- Call `db.commit()` exactly once, at the end of the use case — never inside a repository.
- Services may call infrastructure clients (e.g. LLM, external APIs) but must not be called by them.
- Never put query logic in a service — delegate all DB access to repositories.
