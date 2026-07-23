# Writing Containers

This document describes how to implement and extend the composition root in this project.

## Purpose

Containers live in `app/container/` and are the only place where infrastructure dependencies are wired together. They are the composition root — use cases and route handlers never instantiate infrastructure objects directly.

## Structure

There are two levels:

- `ApplicationContainer` — top-level, application-scoped. Created once at startup and stored on `app.state`. Composes all domain-scoped containers.
- Domain container (e.g. `SupportContainer`) — one per domain. Holds shared infrastructure singletons and builds fresh use case instances per request.

### Domain container

```python
from sqlalchemy.orm import Session

from app.application.<domain>.<use_case> import MyUseCase
from app.config.settings import settings
from app.infrastructure.ai.chat.openai import OpenAIChatModel
from app.infrastructure.database.sqlalchemy.postgresql.unit_of_work.<domain> import (
    SqlAlchemy<Domain>UnitOfWork,
)


class MyDomainContainer:
    """Lazy provider for all <domain> use cases.

    Holds shared infrastructure singletons and builds fresh use case instances
    on every call. Nothing is instantiated until a method is called.
    """

    def __init__(self) -> None:
        """Initialize shared singletons."""
        self._chat_model = OpenAIChatModel()

    def my_use_case(self, db: Session) -> MyUseCase:
        """Build a fresh MyUseCase bound to the given session.

        Args:
            db: Active database session for this request.

        Returns:
            A fully wired MyUseCase instance.
        """
        return MyUseCase(
            uow=SqlAlchemy<Domain>UnitOfWork(db),
            chat_model=self._chat_model,
        )
```

### ApplicationContainer

```python
from app.container.<domain> import MyDomainContainer


class ApplicationContainer:
    """Top-level application-scoped container.

    Created once at startup and stored on app.state. Composes all
    domain-scoped containers. Route handlers access the specific domain
    container they need via the corresponding attribute.
    """

    def __init__(self) -> None:
        self.<domain> = MyDomainContainer()
```

## Singleton vs. per-request

| What | Lifetime | Reason |
|------|----------|--------|
| Infrastructure clients (chat model, embedding model, chunk strategy) | Singleton — created in `__init__` | Stateless; safe to share across requests |
| Use case instances | Per-request — created in the method | Receive a `Session`; must not be shared |
| `Session`-bound objects (UoW, vector store, tool registry) | Per-request — created in the method | Tied to a single database transaction |

## Adding a new domain

1. Create `app/container/<domain>.py` with a domain container class following the structure above.
2. Add the domain container as an attribute of `ApplicationContainer` in `app/container/__init__.py`.
3. Access it in route handlers via `container.<domain>.<use_case>(db)`.

## Rules

- Containers must not contain business logic — only wiring.
- Shared singletons are instantiated in `__init__`; per-request objects are instantiated inside the method.
- Every method on a domain container must accept a `Session` and return a fully wired use case instance.
- Route handlers and CLI commands must never import concrete infrastructure classes — they access use cases only through the container.
- All public methods must have docstrings.
