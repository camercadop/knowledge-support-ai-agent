import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    """Represents a knowledge base document in the application layer."""

    id: uuid.UUID
    title: str
    source: str | None
    content: str
