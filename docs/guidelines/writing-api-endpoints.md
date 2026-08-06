# Writing API Endpoints

This document describes how to implement a route handler in this project.

## Purpose

Route handlers live in `app/api/` and are the entry point for all HTTP requests. They parse the request, wire dependencies, delegate to a use case, and return the response.

## Structure

```python
import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.container.my_domain import MyDomainContainer
from app.infrastructure.database.sqlalchemy.postgresql.engine import get_db
from app.schemas.my_domain import MyRequest, MyResponse

router = APIRouter()
logger = logging.getLogger(__name__)


def get_container(request: Request) -> MyDomainContainer:
    """Return the domain container from request state.

    Args:
        request: The current FastAPI request.

    Returns:
        The MyDomainContainer instance stored on app.state.container.my_domain.
    """
    container: MyDomainContainer = request.app.state.container.my_domain
    return container


@router.post("/my-resource", response_model=MyResponse)
def my_endpoint(
    request: MyRequest,
    container: MyDomainContainer = Depends(get_container),
    db: Session = Depends(get_db),
) -> MyResponse:
    """Receive a request and return the result."""
    logger.info("Received request for %s", request.some_identifier)
    result = container.my_use_case(db).handle(request.some_identifier, request.some_field)
    logger.info("Completed request for %s", request.some_identifier)
    return MyResponse(field=result)
```

Register the router in `app/main.py`:

```python
from app.api.my_domain import router as my_domain_router

app.include_router(my_domain_router)
```

## CRUD Endpoints

For resources that expose standard CRUD operations, use the `CRUDRouter` factory
from `app/api/crud.py` instead of writing individual route handlers.

`CRUDRouter` wires `POST`, `GET` (list), `GET` (by id), `PATCH`, and `DELETE`
endpoints from a single call:

```python
from app.infrastructure.routers.crud import CRUDRouter

router = CRUDRouter(
    prefix="/my-resources",
    response_model=MyResponse,
    get_use_case=lambda req, db: get_container(req).my_crud(db),
    to_response=lambda entity: MyResponse(id=entity.id, name=entity.name),
    create_schema=MyCreateRequest,
    update_schema=MyUpdateRequest,
)
```

The `create_schema` and `update_schema` field names must match the use case's
`create()` and `update()` parameter names respectively, as they are forwarded
via `model_dump()`.

Use `CRUDRouter` when the resource maps directly to a `CRUDUseCase`. Write
individual route handlers when the endpoint has domain-specific logic, custom
status codes, or a non-standard request/response shape.

## Rules

- One file per domain, named after the domain (e.g. `chat.py`, `documents.py`).
- The handler must only parse the request, call the container, and return the response — no business logic.
- API files must not contain factory functions, infrastructure wiring helpers, or any logic beyond request parsing and response mapping.
- Always declare `response_model` on the route decorator.
- The database session is always injected via `Depends(get_db)` — never instantiated directly.
- The domain container is always injected via `Depends(get_container)` — never instantiated directly in the handler.
- Log at the start and end of each handler using `%s`-style formatting. See [Writing Logs](writing-logs.md).
- Never call repositories or infrastructure clients directly from a handler — always go through a use case via the container.
