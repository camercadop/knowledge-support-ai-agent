import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models.

    Provides a UUID primary key and automatic created_at/updated_at timestamps.
    All models must inherit from this class instead of DeclarativeBase directly.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        # Primary key, generated automatically on insert
        primary_key=True,
        default=uuid.uuid4,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        # Set automatically on insert
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        # Set automatically on insert and updated on every change
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
