import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class Contact:
    """Represents a contact in the application layer."""

    id: uuid.UUID
    phone: str
