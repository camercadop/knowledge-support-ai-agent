import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    """Represents a knowledge base document in the application layer."""

    id: uuid.UUID
    title: str
    source: str | None
    content: str
    chunk_count: int = 0
    embedding_model_used: str | None = None
    knowledge_base_id: uuid.UUID | None = None
