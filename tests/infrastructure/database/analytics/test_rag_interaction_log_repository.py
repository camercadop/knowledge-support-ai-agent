import uuid

import pytest
from collections.abc import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.application.support.ports.vector_store import SearchResult
from app.infrastructure.database.sqlalchemy.postgresql.base import Base
from app.infrastructure.database.sqlalchemy.postgresql.models.analytics.base import AnalyticsBase
from app.infrastructure.database.sqlalchemy.postgresql.repositories.analytics.rag_interaction_log import (  # noqa: E501
    RagInteractionLogRepository,
)

import os

_TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/knowledge_agent",
)


@pytest.fixture(scope="module")
def analytics_engine() -> Generator[Engine]:
    """Yield a SQLAlchemy engine with both Base and AnalyticsBase tables created."""
    eng = create_engine(_TEST_DATABASE_URL)
    with eng.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS analytics"))
        conn.commit()
    Base.metadata.create_all(bind=eng)
    AnalyticsBase.metadata.create_all(bind=eng)
    yield eng
    AnalyticsBase.metadata.drop_all(bind=eng)
    eng.dispose()


@pytest.fixture()
def analytics_db(analytics_engine: Engine) -> Generator[Session]:
    """Yield a session that rolls back after each test."""
    connection = analytics_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    session.begin_nested()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


_CONV_ID = uuid.uuid4()


@pytest.fixture()
def repo(analytics_db: Session) -> RagInteractionLogRepository:
    return RagInteractionLogRepository(analytics_db)


def _create(repo: RagInteractionLogRepository, **kwargs: object):  # type: ignore[no-untyped-def]
    defaults: dict[str, object] = {
        "conversation_id": _CONV_ID,
        "question": "q",
        "answer": "a",
        "model_used": "gpt-4o-mini",
        "chunks": None,
        "prompt_tokens": None,
        "completion_tokens": None,
    }
    defaults.update(kwargs)
    return repo.create(**defaults)  # type: ignore[arg-type]


# --- create ---


def test_create_returns_log_with_correct_fields(repo: RagInteractionLogRepository) -> None:
    log = _create(repo, question="what is rag?", answer="rag answer", model_used="gpt-4o")

    assert log.conversation_id == _CONV_ID
    assert log.question == "what is rag?"
    assert log.answer == "rag answer"
    assert log.model_used == "gpt-4o"


def test_create_assigns_id(repo: RagInteractionLogRepository) -> None:
    log = _create(repo)
    assert log.id is not None


def test_create_assigns_created_at(repo: RagInteractionLogRepository) -> None:
    log = _create(repo)
    assert log.created_at is not None


def test_create_persists_token_counts(repo: RagInteractionLogRepository) -> None:
    log = _create(repo, prompt_tokens=15, completion_tokens=7)

    assert log.prompt_tokens == 15
    assert log.completion_tokens == 7


def test_create_persists_chunks(repo: RagInteractionLogRepository) -> None:
    chunk = SearchResult(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        chunk="some context",
        score=0.9,
        document_title="Test Doc",
        source=None,
    )
    log = _create(repo, chunks=[chunk])

    assert log.chunks is not None
    assert log.chunks[0].chunk == "some context"
    assert log.chunks[0].score == 0.9


def test_create_with_none_chunks(repo: RagInteractionLogRepository) -> None:
    log = _create(repo, chunks=None)
    assert log.chunks is None


# --- list_all ---


def test_list_all_returns_empty_when_no_logs(repo: RagInteractionLogRepository) -> None:
    assert repo.list_all() == []


def test_list_all_returns_all_created_logs(repo: RagInteractionLogRepository) -> None:
    _create(repo, question="first")
    _create(repo, question="second")

    logs = repo.list_all()

    assert len(logs) == 2
    questions = {log.question for log in logs}
    assert questions == {"first", "second"}


def test_list_all_deserializes_chunks(repo: RagInteractionLogRepository) -> None:
    chunk_id = uuid.uuid4()
    chunk = SearchResult(
        chunk_id=chunk_id,
        document_id=uuid.uuid4(),
        chunk="context text",
        score=0.75,
        document_title="Test Doc",
        source=None,
    )
    _create(repo, chunks=[chunk])

    logs = repo.list_all()

    assert logs[0].chunks is not None
    assert logs[0].chunks[0].chunk_id == chunk_id
    assert logs[0].chunks[0].chunk == "context text"
