import uuid
from dataclasses import dataclass
from datetime import datetime

from app.application.support.ports.vector_store import SearchResult


@dataclass(frozen=True)
class RagInteractionLog:
    """Represents a recorded RAG pipeline turn in the application layer."""

    id: uuid.UUID
    conversation_id: uuid.UUID
    question: str
    answer: str
    model_used: str
    chunks: list[SearchResult] | None
    prompt_tokens: int | None
    completion_tokens: int | None
    created_at: datetime
