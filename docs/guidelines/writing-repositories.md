# Repository Pattern

This document describes how to implement a repository in this project.

## Purpose

Repositories are the only layer allowed to access the database directly. They encapsulate all query logic and expose a clean interface to the application layer.

## Structure

```python
from sqlalchemy.orm import Session
from app.models.my_model import MyModel


class MyModelRepository:
    """Handles persistence operations for MyModel entities."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self._db = db

    def get_by_id(self, id: uuid.UUID) -> MyModel | None:
        """Return the entity with the given id, or None if not found."""
        return self._db.query(MyModel).filter(MyModel.id == id).first()

    def create(self, ...) -> MyModel:
        """Persist a new entity and return it."""
        entity = MyModel(...)
        self._db.add(entity)
        self._db.flush()
        return entity
```

## Rules

- The constructor always receives a `Session` and stores it as `self._db`.
- Use `flush()` after adding a new entity — never `commit()`.
- The caller (application service) owns the transaction and is responsible for calling `commit()`.
- Never import or call application services from a repository.
- One repository per model.

## Transaction Boundary

Repositories flush changes to make them visible within the current transaction (e.g. to get the generated `id`), but they never commit. The application service commits once at the end of the use case:

```python
# service
self._repository.create(...)   # flush only
self._db.commit()              # commit owned by the service
```
