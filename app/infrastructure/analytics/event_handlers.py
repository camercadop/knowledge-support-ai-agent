from app.application.analytics.ports.unit_of_work.analytics import AnalyticsUnitOfWork
from app.application.support.events.question_answered import QuestionAnswered


class RagInteractionLogHandler:
    """Persists a RAG interaction log entry when a QuestionAnswered event is received.

    Args:
        uow: Transactional boundary for the analytics domain.
    """

    def __init__(self, uow: AnalyticsUnitOfWork) -> None:
        self._uow = uow

    def handle(self, event: QuestionAnswered) -> None:
        """Persist a RAG interaction log entry from the event payload.

        Args:
            event: The QuestionAnswered event raised after a completed chat turn.
        """
        self._uow.rag_interaction_logs.create(
            conversation_id=event.conversation_id,
            question=event.question,
            answer=event.answer,
            model_used=event.model_used,
            chunks=event.chunks,
            prompt_tokens=event.prompt_tokens,
            completion_tokens=event.completion_tokens,
        )
        self._uow.commit()
