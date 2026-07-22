# Dependency Injection

This document describes how dependencies are wired in this project.

## Overview

The project uses two complementary mechanisms:

- **FastAPI `Depends`** — for request-scoped dependencies (database session).
- **Module-level singletons** — for stateless, long-lived infrastructure clients (LLM, embedding model).

Use cases are constructed inline in the route handler, receiving both.

## Database Session

`get_db` in `app/infrastructure/database/engine.py` yields a `Session` per request and closes it after the response:

```python
@router.post("/my-resource")
def my_endpoint(request: MyRequest, db: Session = Depends(get_db)) -> MyResponse:
    uow = SqlAlchemyUnitOfWork(db)
    ...
```

Never instantiate `SessionLocal` directly in a handler or use case.

## Stateless Infrastructure Clients

Clients with no per-request state are instantiated once at module level in the router file:

```python
# app/api/my_domain.py
_chat_model = OpenAIChatModel()

@router.post("/my-resource")
def my_endpoint(request: MyRequest, db: Session = Depends(get_db)) -> MyResponse:
    use_case = DoSomething(uow=SqlAlchemyUnitOfWork(db), chat_model=_chat_model)
    ...
```

## Use Case Wiring

Use cases are constructed inline in the handler — never registered as FastAPI dependencies. The handler is the composition root:

```python
use_case = DoSomething(
    uow=SqlAlchemyUnitOfWork(db),
    chat_model=_chat_model,
)
```

In tests, pass fake implementations directly:

```python
use_case = DoSomething(
    uow=FakeUnitOfWork(),
    chat_model=FakeChatModel(),
)
```

## Factories

When constructing a dependency requires non-trivial logic (e.g. selecting an implementation based on a setting), extract it into a factory function in `app/infrastructure/`. Import and call it from the route handler or `app/cli/deps.py` — never define it inline in an API file.


## Adding a New Infrastructure Dependency

1. Define the port (abstract class) in `app/application/ports/`.
2. Implement it in `app/infrastructure/`.
3. If stateless, instantiate it at module level in the router.
4. Pass it into the use case constructor.

## Rules

- `Depends(get_db)` is the only FastAPI dependency used — do not register use cases or repositories as FastAPI dependencies.
- Use cases receive all dependencies through their constructor — never resolve them internally.
- Concrete infrastructure types are never imported inside `app/application/`.
