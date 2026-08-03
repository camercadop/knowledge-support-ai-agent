import pytest
from sqlalchemy.orm import Session

from app.application.support.use_cases.clear_history import ClearHistory
from app.infrastructure.database.sqlalchemy.postgresql.unit_of_work.messaging import (
    SqlAlchemyMessagingUnitOfWork,
)
from app.infrastructure.observability.instrumentation import NullInstrumentation

_PHONE = "+1234567890"


@pytest.fixture()
def uow(pg_db: Session) -> SqlAlchemyMessagingUnitOfWork:
    """Return a MessagingUnitOfWork backed by the PostgreSQL session."""
    return SqlAlchemyMessagingUnitOfWork(pg_db)


def _make_use_case(uow: SqlAlchemyMessagingUnitOfWork) -> ClearHistory:
    return ClearHistory(uow=uow, instrumentation=NullInstrumentation())


def test_clear_history_deletes_all_messages(uow: SqlAlchemyMessagingUnitOfWork) -> None:
    contact = uow.contacts.get_or_create_by_phone(_PHONE)
    conversation = uow.conversations.get_or_create_for_contact(contact.id)
    uow.messages.create(conversation_id=conversation.id, role="user", content="hello", tokens=None)
    uow.commit()

    _make_use_case(uow).handle(_PHONE)

    messages = uow.messages.list_by_conversation(conversation.id)
    assert messages == []


def test_clear_history_does_not_raise_when_no_messages(uow: SqlAlchemyMessagingUnitOfWork) -> None:
    _make_use_case(uow).handle(_PHONE)


def test_clear_history_creates_contact_if_not_exists(uow: SqlAlchemyMessagingUnitOfWork) -> None:
    _make_use_case(uow).handle("+9999999999")
    contact = uow.contacts.get_or_create_by_phone("+9999999999")
    assert contact.phone == "+9999999999"
