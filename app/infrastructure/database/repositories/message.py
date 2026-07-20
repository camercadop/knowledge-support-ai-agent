import uuid

from sqlalchemy.orm import Session

from app.application.ports.repositories.message import AbstractMessageRepository
from app.infrastructure.database.models.message import Message


class MessageRepository(AbstractMessageRepository):
    """Handles persistence operations for Message entities."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self._db = db

    def list_by_conversation(self, conversation_id: uuid.UUID) -> list[Message]:
        """Return all messages for a conversation ordered by creation time."""
        return (
            self._db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .all()
        )

    def create(
        self,
        conversation_id: uuid.UUID,
        role: str,
        content: str,
        tokens: int | None = None,
    ) -> Message:
        """Persist a new message and return it."""
        message = Message(
            conversation_id=conversation_id, role=role, content=content, tokens=tokens
        )
        self._db.add(message)
        self._db.flush()
        return message
