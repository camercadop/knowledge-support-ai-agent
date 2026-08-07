import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.application.analytics.models.rag_interaction_log import RagInteractionLog
from app.application.analytics.ports.repositories.rag_interaction_log import (
    AbstractRagInteractionLogRepository,
)
from app.application.analytics.use_cases.record_rag_interaction import (
    RecordRagInteraction,
)
from app.application.shared.ports.unit_of_work import UnitOfWork
from app.application.support.events.context_compressed import ContextCompressed
from app.application.support.events.question_answered import QuestionAnswered
from app.application.support.ports.vector_store import SearchResult
from app.infrastructure.analytics.event_handlers import (
    CompressionAnalyticsHandler,
    RagInteractionLogHandler,
)


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


class FakeUnitOfWork(UnitOfWork):
    """In-memory fake UoW for testing."""

    def __init__(self) -> None:
        self._repo = FakeRagInteractionLogRepository()
        self.committed = False

    def get[R](self, repo_type: type[R]) -> R:
        """Return the repository instance for the given port type."""
        return self._repo  # type: ignore[return-value]

    def commit(self) -> None:
        """Mark the unit of work as committed."""
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


def _make_compression_event(**kwargs: object) -> ContextCompressed:
    defaults: dict[str, object] = {
        "conversation_id": uuid.uuid4(),
        "strategy": "token_limit",
        "compression_ratio": 0.6,
        "original_chunk_count": 5,
        "compressed_chunk_count": 3,
    }
    defaults.update(kwargs)
    return ContextCompressed(**defaults)  # type: ignore[arg-type]


# --- RagInteractionLogHandler ---


def test_handler_delegates_to_use_case() -> None:
    use_case = MagicMock(spec=RecordRagInteraction)
    handler = RagInteractionLogHandler(use_case=use_case)
    event = _make_event()

    handler.handle(event)

    use_case.handle.assert_called_once_with(event)


# --- RecordRagInteraction ---


def test_persists_log_from_event() -> None:
    uow = FakeUnitOfWork()
    use_case = RecordRagInteraction(uow=uow)

    use_case.handle(_make_event(question="what is rag?", answer="rag answer"))

    assert len(uow._repo._logs) == 1
    log = uow._repo._logs[0]
    assert log.question == "what is rag?"
    assert log.answer == "rag answer"


def test_commits_after_persisting() -> None:
    uow = FakeUnitOfWork()
    use_case = RecordRagInteraction(uow=uow)

    use_case.handle(_make_event())

    assert uow.committed is True


def test_persists_model_used_from_event() -> None:
    uow = FakeUnitOfWork()
    use_case = RecordRagInteraction(uow=uow)

    use_case.handle(_make_event(model_used="gpt-4o"))

    assert uow._repo._logs[0].model_used == "gpt-4o"


def test_persists_token_counts_from_event() -> None:
    uow = FakeUnitOfWork()
    use_case = RecordRagInteraction(uow=uow)

    use_case.handle(_make_event(prompt_tokens=20, completion_tokens=8))

    log = uow._repo._logs[0]
    assert log.prompt_tokens == 20
    assert log.completion_tokens == 8


def test_persists_chunks_from_event() -> None:
    uow = FakeUnitOfWork()
    use_case = RecordRagInteraction(uow=uow)
    chunk = SearchResult(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        chunk="some context",
        score=0.85,
        document_title="Test Doc",
        source=None,
    )

    use_case.handle(_make_event(chunks=[chunk]))

    log = uow._repo._logs[0]
    assert log.chunks is not None
    assert log.chunks[0].chunk == "some context"


def test_persists_none_chunks_when_no_context() -> None:
    uow = FakeUnitOfWork()
    use_case = RecordRagInteraction(uow=uow)

    use_case.handle(_make_event(chunks=None))

    assert uow._repo._logs[0].chunks is None


# --- CompressionAnalyticsHandler ---


def test_compression_handler_logs_strategy(caplog: pytest.LogCaptureFixture) -> None:
    handler = CompressionAnalyticsHandler()
    event = _make_compression_event(strategy="token_limit")

    with caplog.at_level("INFO", logger="app.infrastructure.analytics.event_handlers"):
        handler.handle(event)

    assert "token_limit" in caplog.text


def test_compression_handler_logs_ratio(caplog: pytest.LogCaptureFixture) -> None:
    handler = CompressionAnalyticsHandler()
    event = _make_compression_event(compression_ratio=0.6)

    with caplog.at_level("INFO", logger="app.infrastructure.analytics.event_handlers"):
        handler.handle(event)

    assert "0.600" in caplog.text


def test_compression_handler_logs_chunk_counts(caplog: pytest.LogCaptureFixture) -> None:
    handler = CompressionAnalyticsHandler()
    event = _make_compression_event(original_chunk_count=10, compressed_chunk_count=4)

    with caplog.at_level("INFO", logger="app.infrastructure.analytics.event_handlers"):
        handler.handle(event)

    assert "10" in caplog.text
    assert "4" in caplog.text
