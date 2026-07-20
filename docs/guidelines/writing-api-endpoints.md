# Writing API Endpoints

This document describes how to implement a route handler in this project.

## Purpose

Route handlers live in `app/api/` and are the entry point for all HTTP requests. They parse the request, wire dependencies, delegate to a use case, and return the response.

## Structure

```python
import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.application.my_domain.do_something import DoSomething
from app.infrastructure.database.engine import get_db
from app.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from app.schemas.my_domain import MyRequest, MyResponse

router = APIRouter()
logger = logging.getLogger(__name__)

_my_client = MyInfrastructureClient()


@router.post("/my-resource", response_model=MyResponse)
def my_endpoint(request: MyRequest, db: Session = Depends(get_db)) -> MyResponse:
    """Receive a request and return the result."""
    logger.info("Received request for %s", request.some_identifier)
    use_case = DoSomething(uow=SqlAlchemyUnitOfWork(db), client=_my_client)
    result = use_case.handle(request.some_identifier, request.some_field)
    return MyResponse(field=result)
```

Register the router in `app/main.py`:

```python
from app.api.my_domain import router as my_domain_router

app.include_router(my_domain_router)
```

## Rules

- One file per domain, named after the domain (e.g. `chat.py`, `documents.py`).
- The handler must only parse the request, wire the use case, and return the response — no business logic.
- Always declare `response_model` on the route decorator.
- Infrastructure clients that are stateless and thread-safe (e.g. `OpenAIChatModel`) are instantiated once at module level.
- The database session is always injected via `Depends(get_db)` — never instantiated directly.
- Log at the start and end of each handler using `%s`-style formatting. See [Writing Logs](writing-logs.md).
- Never call repositories or infrastructure clients directly from a handler — always go through a use case.
