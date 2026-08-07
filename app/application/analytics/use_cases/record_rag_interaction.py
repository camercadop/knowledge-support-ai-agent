from app.application.analytics.models.rag_interaction_log import RagInteractionLog
from app.application.analytics.ports.repositories.rag_interaction_log import (
    AbstractRagInteractionLogRepository,
)
from app.application.shared.ports.unit_of_work import UnitOfWork
from app.application.support.events.question_answered import QuestionAnswered


class RecordRagInteraction:
    """Persists a RAG interaction log entry from a QuestionAnswered event.

    Args:
        uow: Transactional boundary for the analytics domain.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def handle(self, event: QuestionAnswered) -> RagInteractionLog:
        """Persist the interaction log and commit the transaction.

        Args:
            event: The QuestionAnswered event carrying all log fields.

        Returns:
            The persisted RagInteractionLog entry.
        """
        log = self._uow.get(AbstractRagInteractionLogRepository).create(  # type: ignore[type-abstract]
            conversation_id=event.conversation_id,
            question=event.question,
            answer=event.answer,
            model_used=event.model_used,
            chunks=event.chunks,
            prompt_tokens=event.prompt_tokens,
            completion_tokens=event.completion_tokens,
        )
        self._uow.commit()
        return log
