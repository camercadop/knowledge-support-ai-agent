# Repository Pattern

This document describes how to implement a repository in this project.

## Purpose

Repositories are the only layer allowed to access the database directly. They encapsulate all query logic and expose a clean interface to the application layer.

## Structure

```python
from sqlalchemy.orm import Session

from app.application.models.my_model import MyModel
from app.application.ports.repositories.my_model import AbstractMyModelRepository
from app.infrastructure.database.models.my_model import MyModel as MyModelORM


class MyModelRepository(AbstractMyModelRepository):
    """Handles persistence operations for MyModel entities."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self._db = db

    def get_by_id(self, id: uuid.UUID) -> MyModel | None:
        """Return the entity with the given id, or None if not found."""
        orm = self._db.query(MyModelORM).filter(MyModelORM.id == id).first()
        if orm is None:
            return None
        return MyModel(id=orm.id, ...)

    def create(self, ...) -> MyModel:
        """Persist a new entity and return it."""
        orm = MyModelORM(...)
        self._db.add(orm)
        self._db.flush()
        return MyModel(id=orm.id, ...)
```

## Rules

- The constructor always receives a `Session` and stores it as `self._db`.
- Use `flush()` after adding a new entity — never `commit()`.
- The caller (use case) owns the transaction and is responsible for calling `uow.commit()`.
- Never import or call application services from a repository.
- One repository per model.
- Every repository must implement the corresponding abstract port defined in `app/application/ports/repositories/` — never expose a concrete repository class directly to the application layer.
- Never return ORM model instances to the application layer — always map to the corresponding application model in `app/application/models/`.

## Transaction Boundary

Repositories flush changes to make them visible within the current transaction (e.g. to get the generated `id`), but they never commit. The use case commits once at the end via the `UnitOfWork`:

```python
# use case
self._uow.my_entities.create(...)  # flush only
self._uow.commit()                 # commit owned by the use case
```
