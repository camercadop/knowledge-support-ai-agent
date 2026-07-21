from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.sqlalchemy.postgresql.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.sqlalchemy.postgresql.models.conversation import Conversation


class Contact(Base):
    """Represents a user who interacts with the agent via WhatsApp."""

    __tablename__ = "contacts"

    phone: Mapped[str] = mapped_column(
        # WhatsApp phone number, used as the unique identifier for the contact
        unique=True,
        nullable=False,
    )
    name: Mapped[str | None] = mapped_column(
        # Display name of the contact
        nullable=True,
    )

    conversations: Mapped[list["Conversation"]] = relationship(back_populates="contact")  # noqa: F821
