from app.application.analytics.use_cases.record_rag_interaction import (
    RecordRagInteraction,
)
from app.application.support.events.question_answered import QuestionAnswered


class RagInteractionLogHandler:
    def __init__(self, use_case: RecordRagInteraction) -> None:
        self._use_case = use_case

    def handle(self, event: QuestionAnswered) -> None:
        self._use_case.handle(event)
