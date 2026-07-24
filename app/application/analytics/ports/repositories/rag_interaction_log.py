import uuid
from abc import ABC, abstractmethod

from app.application.analytics.models.rag_interaction_log import RagInteractionLog
from app.application.support.ports.vector_store import SearchResult


class AbstractRagInteractionLogRepository(ABC):
    """Port that defines the contract for RAG interaction log persistence."""

    @abstractmethod
    def create(
        self,
        conversation_id: uuid.UUID,
        question: str,
        answer: str,
        model_used: str,
        chunks: list[SearchResult] | None,
        prompt_tokens: int | None,
        completion_tokens: int | None,
    ) -> RagInteractionLog:
        """Persist a new RAG interaction log entry and return it."""

    @abstractmethod
    def list_all(self) -> list[RagInteractionLog]:
        """Return all recorded RAG interaction logs."""
