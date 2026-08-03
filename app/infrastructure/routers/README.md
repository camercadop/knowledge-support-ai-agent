# routers

This sub-package contains reusable FastAPI router factories.

## Modules

- `crud.py` — `CRUDRouter` factory; builds a fully wired `APIRouter` with `POST`, `GET` (list), `GET` (by id), `PATCH`, and `DELETE` endpoints for any `CRUDUseCase`
