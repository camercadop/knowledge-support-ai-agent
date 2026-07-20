from typing import TYPE_CHECKING

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.document_chunk import DocumentChunk


class Document(Base):
    """Represents a knowledge base document that can be chunked and indexed."""

    __tablename__ = "documents"

    title: Mapped[str] = mapped_column(
        # Human-readable title of the document
        nullable=False,
    )
    source: Mapped[str | None] = mapped_column(
        # Origin of the document (e.g. file path, URL)
        nullable=True,
    )
    content: Mapped[str] = mapped_column(
        # Full raw text content of the document
        Text,
        nullable=False,
    )

    chunks: Mapped[list["DocumentChunk"]] = relationship(back_populates="document")
