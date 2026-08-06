# Repository Pattern

This document describes how to implement a repository in this project.

## Purpose

Repositories are the only layer allowed to access the database directly. They encapsulate all query logic and expose a clean interface to the application layer.

## Base Class

All SQLAlchemy repositories extend `SqlAlchemyRepository`, defined in
`app/infrastructure/database/sqlalchemy/postgresql/repositories/base.py`.

The base class provides:

- `__init__(self, db: Session)` — stores the session as `self._db`
- `_orm_class: type[OrmT]` — declared once per subclass; used by the default method implementations
- `_to_domain(orm: OrmT) -> DomainT` — abstract; subclasses implement the ORM-to-domain mapping
- `_persist(**kwargs) -> DomainT` — instantiates `_orm_class` with a generated UUID and the given kwargs, flushes, and returns the domain model
- `get_by_id(entity_id) -> DomainT | None` — default implementation using `_orm_class` and `_to_domain`
- `list() -> list[DomainT]` — default implementation using `_orm_class` and `_to_domain`
- `update(entity, **changes) -> DomainT | None` — default implementation using `_orm_class` and `_to_domain`
- `delete(entity_id) -> None` — default implementation using `_orm_class`

Override any of these only when the behaviour needs to differ from the default.

## Abstract Port

Every repository must implement the corresponding abstract port defined in
`app/application/<domain>/ports/repositories/`. Abstract ports extend the shared
`Repository` marker base from `app/application/shared/ports/repository.py` instead
of `ABC` directly:

```python
from app.application.shared.ports.repository import Repository


class AbstractMyModelRepository(Repository):
    """Port that defines the contract for MyModel persistence."""

    @abstractmethod
    def create(self, name: str) -> MyModel: ...
```

## Structure

```python
from app.application.models.my_model import MyModel
from app.application.ports.repositories.my_model import AbstractMyModelRepository
from app.infrastructure.database.models.my_model import MyModel as MyModelORM
from app.infrastructure.database.sqlalchemy.postgresql.repositories.base import (
    SqlAlchemyRepository,
)


class MyModelRepository(
    SqlAlchemyRepository[MyModelORM, MyModel],
    AbstractMyModelRepository,
):
    """Handles persistence operations for MyModel entities."""

    _orm_class = MyModelORM

    def _to_domain(self, orm: MyModelORM) -> MyModel:
        """Translate a MyModel ORM row into its domain model counterpart."""
        return MyModel(id=orm.id, name=orm.name)

    def create(self, name: str) -> MyModel:
        """Persist a new entity and return it."""
        return self._persist(name=name)
```

Methods already provided by the base (`get_by_id`, `list`, `update`, `delete`) do not
need to be re-implemented unless the behaviour differs.

## Rules

- Extend `SqlAlchemyRepository[OrmT, DomainT]` and the corresponding abstract port.
- Declare `_orm_class` once at class level — never reference the ORM class directly in methods.
- Implement `_to_domain` to map ORM rows to domain models — never inline the mapping in individual methods.
- Use `_persist(**kwargs)` for create operations — never call `self._db.add` + `self._db.flush` manually.
- Use `flush()` after adding a new entity — never `commit()`.
- The caller (use case) owns the transaction and is responsible for calling `uow.commit()`.
- Never import or call application services from a repository.
- One repository per model.
- Never return ORM model instances to the application layer — always map to the corresponding application model in `app/application/<domain>/models/`.

## Registration

Every concrete repository must register itself against its abstract port using the `@repository` decorator from `app/infrastructure/database/sqlalchemy/postgresql/repositories/registry.py`:

```python
from app.infrastructure.database.sqlalchemy.postgresql.repositories.registry import (
    repository,
)

@repository(AbstractMyModelRepository)
class MyModelRepository(
    SqlAlchemyRepository[MyModelORM, MyModel],
    AbstractMyModelRepository,
):
    ...
```

No manual registration in `__init__.py` is needed — all modules in the repositories package are auto-imported at startup via `pkgutil.iter_modules`, so the decorator runs automatically as long as the module is placed in `app/infrastructure/database/sqlalchemy/postgresql/repositories/`.

## Transaction Boundary

Repositories flush changes to make them visible within the current transaction (e.g. to get the generated `id`), but they never commit. The use case resolves repositories via `uow.get()` and commits once at the end:

```python
# use case
self._uow.get(AbstractMyModelRepository).create(...)  # flush only
self._uow.commit()                                    # commit owned by the use case
```
