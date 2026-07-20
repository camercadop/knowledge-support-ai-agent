from abc import ABC, abstractmethod

from app.application.ports.repositories.contact import AbstractContactRepository
from app.application.ports.repositories.conversation import (
    AbstractConversationRepository,
)
from app.application.ports.repositories.message import AbstractMessageRepository


class UnitOfWork(ABC):
    """Port that defines the transactional boundary for a use case.

    Exposes the repositories needed within a single transaction and provides
    an explicit commit(). Implementations live in infrastructure/database/.
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
