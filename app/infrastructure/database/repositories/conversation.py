import uuid

from sqlalchemy.orm import Session

from app.application.ports.repositories.conversation import (
    AbstractConversationRepository,
)
from app.infrastructure.database.models.conversation import Conversation


class ConversationRepository(AbstractConversationRepository):
    """Handles persistence operations for Conversation entities."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self._db = db

    def get_or_create_for_contact(self, contact_id: uuid.UUID) -> Conversation:
        """Return the most recent conversation for a contact, or create one.

        Flushes the session so the new conversation gets an id before commit.
        """
        conversation = (
            self._db.query(Conversation)
            .filter(Conversation.contact_id == contact_id)
            .order_by(Conversation.created_at.desc())
            .first()
        )
        if conversation is None:
            conversation = Conversation(contact_id=contact_id)
            self._db.add(conversation)
            self._db.flush()
        return conversation
