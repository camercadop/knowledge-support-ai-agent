import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeBase:
    """Represents a named, isolated knowledge base."""

    id: uuid.UUID
    name: str
    description: str | None = None
