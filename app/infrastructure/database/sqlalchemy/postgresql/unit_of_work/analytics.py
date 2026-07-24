from sqlalchemy.orm import Session

from app.application.analytics.ports.repositories.rag_interaction_log import (
    AbstractRagInteractionLogRepository,
)
from app.application.analytics.ports.unit_of_work.analytics import AnalyticsUnitOfWork
from app.infrastructure.database.sqlalchemy.postgresql.repositories.analytics.rag_interaction_log import (  # noqa: E501
    RagInteractionLogRepository,
)


class SqlAlchemyAnalyticsUnitOfWork(AnalyticsUnitOfWork):
    """AnalyticsUnitOfWork backed by a SQLAlchemy session."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self._db = db
        self._rag_interaction_logs = RagInteractionLogRepository(db)

    @property
    def rag_interaction_logs(self) -> AbstractRagInteractionLogRepository:
        """Return the RAG interaction log repository bound to the current session."""
        return self._rag_interaction_logs

    def commit(self) -> None:
        """Commit the current session transaction."""
        self._db.commit()
