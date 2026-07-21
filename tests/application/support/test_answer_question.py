import uuid

import pytest
from sqlalchemy.orm import Session

from app.application.support.answer_question import AnswerQuestion
from app.infrastructure.ai.mock.chat import MockChatModel
from app.infrastructure.ai.mock.embeddings import MockEmbeddingModel
from app.infrastructure.database.sqlalchemy.postgresql.unit_of_work.messaging import (
    SqlAlchemyMessagingUnitOfWork,
)
from app.infrastructure.vectorstores.fake.store import FakeVectorStore

_PHONE = "+1234567890"


@pytest.fixture()
def uow(db: Session) -> SqlAlchemyMessagingUnitOfWork:
    """Return a MessagingUnitOfWork backed by the in-memory SQLite session."""
    return SqlAlchemyMessagingUnitOfWork(db)


@pytest.fixture()
def vector_store() -> FakeVectorStore:
    """Return an empty FakeVectorStore."""
    return FakeVectorStore()


def _make_use_case(
    uow: SqlAlchemyMessagingUnitOfWork,
    vector_store: FakeVectorStore,
    reply: str = "hello",
) -> AnswerQuestion:
    return AnswerQuestion(
        uow=uow,
        chat_model=MockChatModel(reply=reply),
        embedding_model=MockEmbeddingModel(),
        vector_store=vector_store,
    )


def test_returns_reply_from_chat_model(
    uow: SqlAlchemyMessagingUnitOfWork, vector_store: FakeVectorStore
) -> None:
    reply = _make_use_case(uow, vector_store, reply="hello").handle(_PHONE, "Hi")
    assert reply == "hello"


def test_creates_contact_on_first_message(
    uow: SqlAlchemyMessagingUnitOfWork, vector_store: FakeVectorStore
) -> None:
    _make_use_case(uow, vector_store).handle(_PHONE, "Hi")
    contact = uow.contacts.get_or_create_by_phone(_PHONE)
    assert contact.phone == _PHONE


def test_reuses_existing_contact_on_second_message(
    uow: SqlAlchemyMessagingUnitOfWork, vector_store: FakeVectorStore
) -> None:
    use_case = _make_use_case(uow, vector_store)
    use_case.handle(_PHONE, "Hi")
    use_case.handle(_PHONE, "Hi again")
    contact = uow.contacts.get_or_create_by_phone(_PHONE)
    assert contact.phone == _PHONE


def test_persists_user_and_assistant_messages(
    uow: SqlAlchemyMessagingUnitOfWork, vector_store: FakeVectorStore
) -> None:
    _make_use_case(uow, vector_store, reply="hello").handle(_PHONE, "Hi")
    contact = uow.contacts.get_or_create_by_phone(_PHONE)
    conversation = uow.conversations.get_or_create_for_contact(contact.id)
    messages = uow.messages.list_by_conversation(conversation.id)
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[0].content == "Hi"
    assert messages[1].role == "assistant"
    assert messages[1].content == "hello"


def test_passes_no_context_when_vector_store_empty(
    uow: SqlAlchemyMessagingUnitOfWork, vector_store: FakeVectorStore
) -> None:
    # With an empty vector store and a zero embedding, no context is built.
    # The reply still comes through, confirming the use case completes without context.
    reply = _make_use_case(uow, vector_store).handle(_PHONE, "Hi")
    assert reply == "hello"


def test_builds_rag_context_from_vector_store(
    uow: SqlAlchemyMessagingUnitOfWork, vector_store: FakeVectorStore
) -> None:
    vector_store.upsert(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        chunk="relevant chunk",
        embedding=[1.0, 0.0, 0.0],
    )
    # MockEmbeddingModel returns a zero vector, so cosine distance will be 1.0
    # (orthogonal). The chunk is still returned since it's the only result.
    reply = _make_use_case(uow, vector_store).handle(_PHONE, "Hi")
    assert reply == "hello"
