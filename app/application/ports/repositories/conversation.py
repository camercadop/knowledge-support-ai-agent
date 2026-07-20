import uuid
from abc import ABC, abstractmethod

from app.infrastructure.database.models.conversation import Conversation


class AbstractConversationRepository(ABC):
    """Port that defines the contract for conversation persistence.

    Implementations live in infrastructure/database/repositories/.
    """

    @abstractmethod
    def get_or_create_for_contact(self, contact_id: uuid.UUID) -> Conversation:
        """Return the most recent conversation for a contact, or create one."""
