# Dependency Injection

This document describes how dependencies are wired in this project.

## Overview

The project uses two complementary mechanisms:

- **Containers** — domain-scoped composition roots that hold shared infrastructure singletons and build fresh use case instances per request. See [Writing Containers](writing-containers.md).
- **FastAPI `Depends`** — for request-scoped values that must be resolved per request: the database session and the domain container.

Use cases are never constructed inline in route handlers. The container is the only place where infrastructure is wired to ports.

## Database Session

`get_db` in `app/infrastructure/database/sqlalchemy/postgresql/engine.py` yields a `Session` per request and closes it after the response:

```python
@router.post("/my-resource")
def my_endpoint(
    request: MyRequest,
    container: MyDomainContainer = Depends(get_container),
    db: Session = Depends(get_db),
) -> MyResponse:
    result = container.my_use_case(db).handle(request.field)
    ...
```

Never instantiate `SessionLocal` directly in a handler or use case.

## Container

The `ApplicationContainer` is created once at startup and stored on `app.state`. Route handlers retrieve the relevant domain container via a `get_container` helper:

```python
def get_container(request: Request) -> MyDomainContainer:
    """Return the domain container from request state."""
    container: MyDomainContainer = request.app.state.container.my_domain
    return container
```

The container method receives the session and returns a fully wired use case:

```python
result = container.my_use_case(db).handle(request.field)
```

## Adding a New Infrastructure Dependency

1. Define the port (abstract class) in `app/application/<domain>/ports/`.
2. Implement it in `app/infrastructure/`.
3. Wire it in the domain container — as a singleton in `_setup` if stateless, or per-request inside the use case method if session-bound.
4. Inject it into the use case constructor inside the container method.

## Testing

In tests, construct use cases directly with fake implementations — no container needed:

```python
use_case = DoSomething(
    uow=FakeUnitOfWork(),
    chat_model=FakeChatModel(),
)
```

For API tests, replace the container on `app.state` before the test client is created:

```python
app.state.container = FakeApplicationContainer()
```

## Rules

- `Depends(get_db)` and `Depends(get_container)` are the only FastAPI dependencies used — do not register use cases or repositories as FastAPI dependencies.
- Use cases receive all dependencies through their constructor — never resolve them internally.
- Concrete infrastructure types are never imported inside `app/application/`.
- Never instantiate infrastructure clients directly in route handlers — always go through the container.
