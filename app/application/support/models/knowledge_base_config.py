import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeBaseConfig:
    """A single configuration key-value pair for a knowledge base."""

    id: uuid.UUID
    knowledge_base_id: uuid.UUID
    key: str
    value: str
