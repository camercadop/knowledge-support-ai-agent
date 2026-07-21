from sqlalchemy.orm import Session

from app.application.ports.repositories.contact import AbstractContactRepository
from app.application.ports.repositories.conversation import (
    AbstractConversationRepository,
)
from app.application.ports.repositories.message import AbstractMessageRepository
from app.application.ports.unit_of_work.messaging import MessagingUnitOfWork
from app.infrastructure.database.repositories.contact import ContactRepository
from app.infrastructure.database.repositories.conversation import ConversationRepository
from app.infrastructure.database.repositories.message import MessageRepository


class SqlAlchemyMessagingUnitOfWork(MessagingUnitOfWork):
    """MessagingUnitOfWork backed by a SQLAlchemy session."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self._db = db
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

    def commit(self) -> None:
        """Commit the current session transaction."""
        self._db.commit()
