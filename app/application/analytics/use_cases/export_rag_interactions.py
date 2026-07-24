from app.application.analytics.models.rag_interaction_log import RagInteractionLog
from app.application.analytics.ports.unit_of_work.analytics import AnalyticsUnitOfWork


class ExportRagInteractions:
    """Returns all recorded RAG interaction logs for export.

    Args:
        uow: Transactional boundary for the analytics domain.
    """

    def __init__(self, uow: AnalyticsUnitOfWork) -> None:
        self._uow = uow

    def handle(self) -> list[RagInteractionLog]:
        """Return all RAG interaction logs ordered by creation time.

        Returns:
            List of all RagInteractionLog entries.
        """
        return self._uow.rag_interaction_logs.list_all()
