import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.sqlalchemy.postgresql.base import Base

if TYPE_CHECKING:
    pass


class KnowledgeBase(Base):
    """Represents a named, isolated knowledge base."""

    __tablename__ = "knowledge_bases"
    __table_args__ = (
        UniqueConstraint("name", name="uq_knowledge_bases_name"),
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
    )
