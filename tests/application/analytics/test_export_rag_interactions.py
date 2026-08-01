import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.application.analytics.models.rag_interaction_log import RagInteractionLog
from app.application.analytics.ports.repositories.rag_interaction_log import (
    AbstractRagInteractionLogRepository,
)
from app.application.analytics.ports.unit_of_work.analytics import AnalyticsUnitOfWork
from app.application.analytics.use_cases.export_rag_interactions import ExportRagInteractions
from app.application.support.ports.vector_store import SearchResult


def _make_log(**kwargs: object) -> RagInteractionLog:
    defaults: dict[str, object] = {
        "id": uuid.uuid4(),
        "conversation_id": uuid.uuid4(),
        "question": "q",
        "answer": "a",
        "model_used": "gpt-4o-mini",
        "chunks": None,
        "prompt_tokens": None,
        "completion_tokens": None,
        "created_at": datetime.now(UTC),
    }
    defaults.update(kwargs)
    return RagInteractionLog(**defaults)  # type: ignore[arg-type]


@dataclass
class FakeRagInteractionLogRepository(AbstractRagInteractionLogRepository):
    """In-memory fake for testing."""

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
        log = _make_log(
            conversation_id=conversation_id,
            question=question,
            answer=answer,
            model_used=model_used,
            chunks=chunks,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )
        self._logs.append(log)
        return log

    def list_all(self) -> list[RagInteractionLog]:
        return list(self._logs)


class FakeAnalyticsUnitOfWork(AnalyticsUnitOfWork):
    """In-memory fake UoW for testing."""

    def __init__(self) -> None:
        self._repo = FakeRagInteractionLogRepository()
        self.committed = False

    @property
    def rag_interaction_logs(self) -> FakeRagInteractionLogRepository:
        return self._repo

    def commit(self) -> None:
        self.committed = True


# --- ExportRagInteractions ---


def test_returns_empty_list_when_no_logs() -> None:
    uow = FakeAnalyticsUnitOfWork()
    result = ExportRagInteractions(uow=uow).handle()
    assert result == []


def test_returns_all_persisted_logs() -> None:
    uow = FakeAnalyticsUnitOfWork()
    log_a = _make_log(question="first")
    log_b = _make_log(question="second")
    uow.rag_interaction_logs._logs = [log_a, log_b]

    result = ExportRagInteractions(uow=uow).handle()

    assert len(result) == 2
    assert result[0].question == "first"
    assert result[1].question == "second"


def test_returns_logs_with_correct_fields() -> None:
    uow = FakeAnalyticsUnitOfWork()
    conv_id = uuid.uuid4()
    log = _make_log(
        conversation_id=conv_id,
        question="what is rag?",
        answer="retrieval augmented generation",
        model_used="gpt-4o-mini",
        prompt_tokens=10,
        completion_tokens=5,
    )
    uow.rag_interaction_logs._logs = [log]

    result = ExportRagInteractions(uow=uow).handle()

    assert result[0].conversation_id == conv_id
    assert result[0].question == "what is rag?"
    assert result[0].answer == "retrieval augmented generation"
    assert result[0].model_used == "gpt-4o-mini"
    assert result[0].prompt_tokens == 10
    assert result[0].completion_tokens == 5


def test_returns_logs_with_chunks() -> None:
    uow = FakeAnalyticsUnitOfWork()
    chunk = SearchResult(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        chunk="some context",
        score=0.9,
        document_title="Test Doc",
        source=None,
    )
    log = _make_log(chunks=[chunk])
    uow.rag_interaction_logs._logs = [log]

    result = ExportRagInteractions(uow=uow).handle()

    assert result[0].chunks is not None
    assert result[0].chunks[0].chunk == "some context"
