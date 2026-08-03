from abc import abstractmethod

from app.application.analytics.ports.repositories.rag_interaction_log import (
    AbstractRagInteractionLogRepository,
)
from app.application.shared.ports.unit_of_work import UnitOfWork


class AnalyticsUnitOfWork(UnitOfWork):
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
