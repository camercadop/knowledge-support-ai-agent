import logging

from app.application.shared.ports.unit_of_work import UnitOfWork
from app.application.support.ports.observability import BaseInstrumentation
from app.application.support.ports.repositories.contact import AbstractContactRepository
from app.application.support.ports.repositories.conversation import (
    AbstractConversationRepository,
)
from app.application.support.ports.repositories.message import AbstractMessageRepository

logger = logging.getLogger(__name__)


class ClearHistory:
    """Deletes all chat messages for the conversation associated with a phone number.

    Args:
        uow: Transactional boundary for contacts, conversations, and messages.
        instrumentation: Observability adapter for recording spans.
    """

    def __init__(
        self,
        uow: UnitOfWork,
        instrumentation: BaseInstrumentation,
    ) -> None:
        self._uow = uow
        self._instrumentation = instrumentation

    def handle(self, phone: str) -> None:
        """Delete all messages for the contact's active conversation.

        Looks up the contact by phone, retrieves their conversation, and deletes
        all associated messages. Does nothing if the contact does not exist.

        Args:
            phone: The contact's phone number used to identify the conversation.
        """
        with self._instrumentation.root_span("clear_history.handle"):
            contact = self._uow.get(AbstractContactRepository).get_or_create_by_phone(  # type: ignore[type-abstract]
                phone
            )
            conversation = self._uow.get(
                AbstractConversationRepository  # type: ignore[type-abstract]
            ).get_or_create_for_contact(contact.id)
            self._uow.get(AbstractMessageRepository).delete_by_conversation(  # type: ignore[type-abstract]
                conversation.id
            )
            self._uow.commit()
            logger.info("Cleared history for conversation %s", conversation.id)
