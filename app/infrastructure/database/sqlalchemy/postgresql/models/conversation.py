import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.sqlalchemy.postgresql.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.sqlalchemy.postgresql.models.contact import Contact
    from app.infrastructure.database.sqlalchemy.postgresql.models.message import Message


class Conversation(Base):
    """Represents a conversation session between a contact and the agent."""

    __tablename__ = "conversations"

    contact_id: Mapped[uuid.UUID] = mapped_column(
        # FK to the contact who owns this conversation
        ForeignKey("contacts.id", ondelete="CASCADE"),
        nullable=False,
    )

    contact: Mapped["Contact"] = relationship(back_populates="conversations")  # noqa: F821
    messages: Mapped[list["Message"]] = relationship(back_populates="conversation")  # noqa: F821
