import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.application.analytics.models.rag_interaction_log import RagInteractionLog
from app.application.analytics.ports.repositories.rag_interaction_log import (
    AbstractRagInteractionLogRepository,
)
from app.application.analytics.ports.unit_of_work.analytics import AnalyticsUnitOfWork
from app.application.support.events.question_answered import QuestionAnswered
from app.application.support.ports.vector_store import SearchResult
from app.infrastructure.analytics.event_handlers import RagInteractionLogHandler


@dataclass
class FakeRagInteractionLogRepository(AbstractRagInteractionLogRepository):
    _logs: list[RagInteractionLog] = field(default_factory=list)

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
        log = RagInteractionLog(
            id=uuid.uuid4(),
            conversation_id=conversation_id,
            question=question,
            answer=answer,
            model_used=model_used,
            chunks=chunks,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            created_at=datetime.now(UTC),
        )
        self._logs.append(log)
        return log

    def list_all(self) -> list[RagInteractionLog]:
        return list(self._logs)


class FakeAnalyticsUnitOfWork(AnalyticsUnitOfWork):
    def __init__(self) -> None:
        self._repo = FakeRagInteractionLogRepository()
        self.committed = False

    @property
    def rag_interaction_logs(self) -> FakeRagInteractionLogRepository:
        return self._repo

    def commit(self) -> None:
        self.committed = True


def _make_event(**kwargs: object) -> QuestionAnswered:
    defaults: dict[str, object] = {
        "conversation_id": uuid.uuid4(),
        "question": "what is rag?",
        "answer": "retrieval augmented generation",
        "model_used": "gpt-4o-mini",
        "chunks": None,
        "prompt_tokens": 10,
        "completion_tokens": 5,
    }
    defaults.update(kwargs)
    return QuestionAnswered(**defaults)  # type: ignore[arg-type]


# --- RagInteractionLogHandler ---


def test_persists_log_from_event() -> None:
    uow = FakeAnalyticsUnitOfWork()
    handler = RagInteractionLogHandler(uow=uow)

    handler.handle(_make_event(question="what is rag?", answer="rag answer"))

    assert len(uow.rag_interaction_logs._logs) == 1
    log = uow.rag_interaction_logs._logs[0]
    assert log.question == "what is rag?"
    assert log.answer == "rag answer"


def test_commits_after_persisting() -> None:
    uow = FakeAnalyticsUnitOfWork()
    handler = RagInteractionLogHandler(uow=uow)

    handler.handle(_make_event())

    assert uow.committed is True


def test_persists_model_used_from_event() -> None:
    uow = FakeAnalyticsUnitOfWork()
    handler = RagInteractionLogHandler(uow=uow)

    handler.handle(_make_event(model_used="gpt-4o"))

    assert uow.rag_interaction_logs._logs[0].model_used == "gpt-4o"


def test_persists_token_counts_from_event() -> None:
    uow = FakeAnalyticsUnitOfWork()
    handler = RagInteractionLogHandler(uow=uow)

    handler.handle(_make_event(prompt_tokens=20, completion_tokens=8))

    log = uow.rag_interaction_logs._logs[0]
    assert log.prompt_tokens == 20
    assert log.completion_tokens == 8


def test_persists_chunks_from_event() -> None:
    uow = FakeAnalyticsUnitOfWork()
    handler = RagInteractionLogHandler(uow=uow)
    chunk = SearchResult(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        chunk="some context",
        score=0.85,
    )

    handler.handle(_make_event(chunks=[chunk]))

    log = uow.rag_interaction_logs._logs[0]
    assert log.chunks is not None
    assert log.chunks[0].chunk == "some context"


def test_persists_none_chunks_when_no_context() -> None:
    uow = FakeAnalyticsUnitOfWork()
    handler = RagInteractionLogHandler(uow=uow)

    handler.handle(_make_event(chunks=None))

    assert uow.rag_interaction_logs._logs[0].chunks is None
