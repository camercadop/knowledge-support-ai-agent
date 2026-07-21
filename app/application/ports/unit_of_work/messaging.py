from abc import ABC, abstractmethod

from app.application.ports.repositories.contact import AbstractContactRepository
from app.application.ports.repositories.conversation import (
    AbstractConversationRepository,
)
from app.application.ports.repositories.message import AbstractMessageRepository


class MessagingUnitOfWork(ABC):
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

    @abstractmethod
    def commit(self) -> None:
        """Persist all changes made within the current transaction."""
