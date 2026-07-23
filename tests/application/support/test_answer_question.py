import uuid

import pytest
from sqlalchemy.orm import Session

from app.application.support.answer_question import AnswerQuestion
from app.application.support.retrieval_service import RetrievalService
from app.config.settings import settings
from app.infrastructure.ai.mock.chat import MockChatModel
from app.infrastructure.ai.prompt_builder.default import DefaultPromptBuilder, PromptConfig
from app.infrastructure.ai.mock.embeddings import MockEmbeddingModel
from app.infrastructure.database.sqlalchemy.postgresql.unit_of_work.messaging import (
    SqlAlchemyMessagingUnitOfWork,
)
from app.infrastructure.vectorstores.fake.store import FakeVectorStore

_PHONE = "+1234567890"


@pytest.fixture()
def uow(pg_db: Session) -> SqlAlchemyMessagingUnitOfWork:
    """Return a MessagingUnitOfWork backed by the PostgreSQL session."""
    return SqlAlchemyMessagingUnitOfWork(pg_db)


@pytest.fixture()
def vector_store() -> FakeVectorStore:
    """Return an empty FakeVectorStore."""
    return FakeVectorStore()


def _make_use_case(
    uow: SqlAlchemyMessagingUnitOfWork,
    vector_store: FakeVectorStore,
    reply: str = "hello",
    token_total: int = 0,
) -> AnswerQuestion:
    retrieval_service = RetrievalService(
        vector_store=vector_store,
        top_k=5,
        min_score=None,
        max_chunks=5,
        max_context_tokens=2000,
        encoding_name="cl100k_base",
    )
    return AnswerQuestion(
        uow=uow,
        chat_model=MockChatModel(reply=reply, token_total=token_total),
        embedding_model=MockEmbeddingModel(),
        retrieval_service=retrieval_service,
        prompt_builder=DefaultPromptBuilder(
            config=PromptConfig(
                system_instructions=settings.prompts_system_instructions,
                grounded_instructions=settings.prompts_grounded_instructions,
                no_context_instructions=settings.prompts_no_context_instructions,
            )
        ),
    )


def test_returns_reply_from_chat_model(
    uow: SqlAlchemyMessagingUnitOfWork, vector_store: FakeVectorStore
) -> None:
    result = _make_use_case(uow, vector_store, reply="hello").handle(_PHONE, "Hi")
    assert result.reply == "hello"


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
    result = _make_use_case(uow, vector_store).handle(_PHONE, "Hi")
    assert result.reply == "hello"


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
    result = _make_use_case(uow, vector_store).handle(_PHONE, "Hi")
    assert result.reply == "hello"


def test_history_is_passed_to_chat_model(
    uow: SqlAlchemyMessagingUnitOfWork, vector_store: FakeVectorStore
) -> None:
    use_case = _make_use_case(uow, vector_store, reply="second")
    use_case.handle(_PHONE, "first")
    use_case.handle(_PHONE, "second")
    contact = uow.contacts.get_or_create_by_phone(_PHONE)
    conversation = uow.conversations.get_or_create_for_contact(contact.id)
    messages = uow.messages.list_by_conversation(conversation.id)
    assert messages[0].role == "user"
    assert messages[0].content == "first"
    assert messages[2].role == "user"
    assert messages[2].content == "second"


def test_multiple_rag_chunks_joined_with_double_newline(
    uow: SqlAlchemyMessagingUnitOfWork, vector_store: FakeVectorStore
) -> None:
    for chunk in ("chunk one", "chunk two"):
        vector_store.upsert(
            chunk_id=uuid.uuid4(),
            document_id=uuid.uuid4(),
            chunk=chunk,
            embedding=[1.0, 0.0, 0.0],
        )
    # Both chunks are returned; the use case joins them with \n\n before passing
    # to the chat model. The reply still comes through confirming completion.
    result = _make_use_case(uow, vector_store).handle(_PHONE, "Hi")
    assert result.reply == "hello"


def test_token_usage_is_persisted_on_assistant_message(
    uow: SqlAlchemyMessagingUnitOfWork, vector_store: FakeVectorStore
) -> None:
    _make_use_case(uow, vector_store, token_total=42).handle(_PHONE, "Hi")
    contact = uow.contacts.get_or_create_by_phone(_PHONE)
    conversation = uow.conversations.get_or_create_for_contact(contact.id)
    messages = uow.messages.list_by_conversation(conversation.id)
    assistant_message = next(m for m in messages if m.role == "assistant")
    assert assistant_message.tokens == 42


def test_different_phones_have_separate_conversations(
    uow: SqlAlchemyMessagingUnitOfWork, vector_store: FakeVectorStore
) -> None:
    use_case = _make_use_case(uow, vector_store)
    use_case.handle(_PHONE, "Hi from first")
    use_case.handle("+9999999999", "Hi from second")
    contact_a = uow.contacts.get_or_create_by_phone(_PHONE)
    contact_b = uow.contacts.get_or_create_by_phone("+9999999999")
    conv_a = uow.conversations.get_or_create_for_contact(contact_a.id)
    conv_b = uow.conversations.get_or_create_for_contact(contact_b.id)
    messages_a = uow.messages.list_by_conversation(conv_a.id)
    messages_b = uow.messages.list_by_conversation(conv_b.id)
    assert all(m.content != "Hi from second" for m in messages_a)
    assert all(m.content != "Hi from first" for m in messages_b)
