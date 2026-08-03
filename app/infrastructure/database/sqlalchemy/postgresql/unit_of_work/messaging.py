from sqlalchemy.orm import Session

from app.application.support.ports.repositories.contact import AbstractContactRepository
from app.application.support.ports.repositories.conversation import (
    AbstractConversationRepository,
)
from app.application.support.ports.repositories.message import AbstractMessageRepository
from app.application.support.ports.unit_of_work.messaging import MessagingUnitOfWork
from app.infrastructure.database.sqlalchemy.postgresql.repositories.contact import (
    ContactRepository,
)
from app.infrastructure.database.sqlalchemy.postgresql.repositories.conversation import (  # noqa: E501
    ConversationRepository,
)
from app.infrastructure.database.sqlalchemy.postgresql.repositories.message import (
    MessageRepository,
)
from app.infrastructure.database.sqlalchemy.postgresql.unit_of_work.base import (
    SqlAlchemyUnitOfWork,
)


class SqlAlchemyMessagingUnitOfWork(SqlAlchemyUnitOfWork, MessagingUnitOfWork):
    """MessagingUnitOfWork backed by a SQLAlchemy session."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        super().__init__(db)
        self._contacts = ContactRepository(db)
        self._conversations = ConversationRepository(db)
        self._messages = MessageRepository(db)

    @property
    def contacts(self) -> AbstractContactRepository:
        """Return the contact repository bound to the current session."""
        return self._contacts

    @property
    def conversations(self) -> AbstractConversationRepository:
        """Return the conversation repository bound to the current session."""
        return self._conversations

    @property
    def messages(self) -> AbstractMessageRepository:
        """Return the message repository bound to the current session."""
        return self._messages
