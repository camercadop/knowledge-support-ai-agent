import uuid

from sqlalchemy.orm import Session

from app.application.models.conversation import Conversation
from app.application.ports.repositories.conversation import AbstractConversationRepository
from app.infrastructure.database.sqlalchemy.postgresql.models.conversation import Conversation as ConversationORM


class ConversationRepository(AbstractConversationRepository):
    """Handles persistence operations for Conversation entities."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self._db = db

    def get_or_create_for_contact(self, contact_id: uuid.UUID) -> Conversation:
        """Return the most recent conversation for a contact, or create one.

        Flushes the session so the new conversation gets an id before commit.
        """
        orm = (
            self._db.query(ConversationORM)
            .filter(ConversationORM.contact_id == contact_id)
            .order_by(ConversationORM.created_at.desc())
            .first()
        )
        if orm is None:
            orm = ConversationORM(contact_id=contact_id)
            self._db.add(orm)
            self._db.flush()
        return Conversation(id=orm.id, contact_id=orm.contact_id)
