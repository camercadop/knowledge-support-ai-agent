import uuid
from abc import ABC, abstractmethod

from app.application.models.message import Message


class AbstractMessageRepository(ABC):
    """Port that defines the contract for message persistence.

    Implementations live in infrastructure/database/repositories/.
    """

    @abstractmethod
    def list_by_conversation(self, conversation_id: uuid.UUID) -> list[Message]:
        """Return all messages for a conversation ordered by creation time."""

    @abstractmethod
    def delete_by_conversation(self, conversation_id: uuid.UUID) -> None:
        """Delete all messages belonging to a conversation."""

    @abstractmethod
    def create(
        self,
        conversation_id: uuid.UUID,
        role: str,
        content: str,
        tokens: int | None = None,
    ) -> Message:
        """Persist a new message and return it."""
