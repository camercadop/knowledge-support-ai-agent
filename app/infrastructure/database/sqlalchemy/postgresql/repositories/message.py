import uuid

from sqlalchemy.orm import Session

from app.application.models.message import Message
from app.application.ports.repositories.message import AbstractMessageRepository
from app.infrastructure.database.sqlalchemy.postgresql.models.message import Message as MessageORM


class MessageRepository(AbstractMessageRepository):
    """Handles persistence operations for Message entities."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self._db = db

    def list_by_conversation(self, conversation_id: uuid.UUID) -> list[Message]:
        """Return all messages for a conversation ordered by creation time."""
        rows = (
            self._db.query(MessageORM)
            .filter(MessageORM.conversation_id == conversation_id)
            .order_by(MessageORM.created_at.asc())
            .all()
        )
        return [
            Message(
                id=r.id,
                conversation_id=r.conversation_id,
                role=r.role,
                content=r.content,
                tokens=r.tokens,
            )
            for r in rows
        ]

    def create(
        self,
        conversation_id: uuid.UUID,
        role: str,
        content: str,
        tokens: int | None = None,
    ) -> Message:
        """Persist a new message and return it."""
        orm = MessageORM(
            conversation_id=conversation_id, role=role, content=content, tokens=tokens
        )
        self._db.add(orm)
        self._db.flush()
        return Message(
            id=orm.id,
            conversation_id=orm.conversation_id,
            role=orm.role,
            content=orm.content,
            tokens=orm.tokens,
        )
