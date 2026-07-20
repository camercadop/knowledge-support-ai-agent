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

After creating or modifying a model, generate a migration:

```bash
uv run alembic revision --autogenerate -m "describe the change"
uv run alembic upgrade head
```
