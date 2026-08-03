from abc import abstractmethod

from app.application.shared.ports.unit_of_work import UnitOfWork
from app.application.support.ports.repositories.contact import AbstractContactRepository
from app.application.support.ports.repositories.conversation import (
    AbstractConversationRepository,
)
from app.application.support.ports.repositories.message import AbstractMessageRepository


class MessagingUnitOfWork(UnitOfWork):
    """Port that defines the transactional boundary for the messaging domain.

    Exposes contact, conversation, and message repositories within a single
    transaction. Implementations live in infrastructure/database/unit_of_work/.
    """

    @property
    @abstractmethod
    def contacts(self) -> AbstractContactRepository:
        """Return the contact repository bound to the current transaction."""

    @property
    @abstractmethod
    def conversations(self) -> AbstractConversationRepository:
        """Return the conversation repository bound to the current transaction."""

    @property
    @abstractmethod
    def messages(self) -> AbstractMessageRepository:
        """Return the message repository bound to the current transaction."""
