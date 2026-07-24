from abc import ABC, abstractmethod

from app.application.analytics.ports.repositories.rag_interaction_log import (
    AbstractRagInteractionLogRepository,
)


class AnalyticsUnitOfWork(ABC):
    """Port that defines the transactional boundary for the analytics domain.

    Exposes the RAG interaction log repository within a single transaction.
    Implementations live in infrastructure/database/unit_of_work/.
    """

    @property
    @abstractmethod
    def rag_interaction_logs(self) -> AbstractRagInteractionLogRepository:
        """
        Return the RAG interaction log repository bound to the current transaction.
        """

    @abstractmethod
    def commit(self) -> None:
        """Persist all changes made within the current transaction."""
