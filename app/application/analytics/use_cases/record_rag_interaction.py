from app.application.analytics.models.rag_interaction_log import RagInteractionLog
from app.application.analytics.ports.unit_of_work.analytics import AnalyticsUnitOfWork
from app.application.support.events.question_answered import QuestionAnswered


class RecordRagInteraction:
    def __init__(self, uow: AnalyticsUnitOfWork) -> None:
        self._uow = uow

    def handle(self, event: QuestionAnswered) -> RagInteractionLog:
        log = self._uow.rag_interaction_logs.create(
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
