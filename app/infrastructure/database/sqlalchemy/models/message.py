import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.sqlalchemy.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.sqlalchemy.models.conversation import Conversation


class Message(Base):
    """Represents a single message within a conversation."""

    __tablename__ = "messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        # FK to the conversation this message belongs to
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(
        # Sender role: 'user', 'assistant', or 'system'
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        # Full text content of the message
        Text,
        nullable=False,
    )
    tokens: Mapped[int | None] = mapped_column(
        # Token count for this message, populated when available
        nullable=True,
    )

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")  # noqa: F821
