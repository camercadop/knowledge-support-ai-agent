import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class Conversation:
    """Represents a conversation in the application layer."""

    id: uuid.UUID
    contact_id: uuid.UUID
