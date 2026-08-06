# Model Guidelines

This document describes how to create a new SQLAlchemy model following project conventions.

## Inheriting from Base

All models must inherit from `Base`, defined in `app/infrastructure/database/base.py`. This provides the UUID primary key and `created_at`/`updated_at` timestamps automatically.

## Structure

```python
from app.infrastructure.database.base import Base
from sqlalchemy.orm import Mapped, mapped_column

class MyModel(Base):
    """One-line description of what this model represents."""

    __tablename__ = "my_models"

    field: Mapped[str] = mapped_column(
        # Explanation of what this field represents
        nullable=False,
    )
```

## Rules

- Table names are lowercase plural.
- Every field must have a comment explaining its purpose.
- Nullable fields must be declared explicitly with `nullable=True`.
- Foreign keys must use `ondelete="CASCADE"`.
- Relationships use `relationship()` with `back_populates`.
- Avoid circular imports between models using `TYPE_CHECKING` guards.

## Adding a Migration

Never write migration files manually. Always autogenerate them.

1. Import the new model in `app/infrastructure/database/sqlalchemy/postgresql/models/__init__.py` and add it to `__all__`. This registers it with `Base.metadata` so autogenerate can detect it.

2. Confirm the current DB state:

```bash
uv run alembic current
```

3. Generate the migration:

```bash
uv run alembic revision --autogenerate -m "describe the change"
```

4. Inspect the generated file and remove any operations unrelated to the current change.

5. Apply and confirm:

```bash
uv run alembic upgrade head
uv run alembic current
```
