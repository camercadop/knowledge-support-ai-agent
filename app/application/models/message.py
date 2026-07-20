import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class Message:
    """Represents a message in the application layer."""

    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    tokens: int | None
