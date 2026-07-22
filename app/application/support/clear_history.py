import logging

from app.application.ports.unit_of_work.messaging import MessagingUnitOfWork

logger = logging.getLogger(__name__)


class ClearHistory:
    """Deletes all chat messages for the conversation associated with a phone number.

    Args:
        uow: Transactional boundary for contacts, conversations, and messages.
    """

    def __init__(self, uow: MessagingUnitOfWork) -> None:
        self._uow = uow

    def handle(self, phone: str) -> None:
        """Delete all messages for the contact's active conversation.

        Looks up the contact by phone, retrieves their conversation, and deletes
        all associated messages. Does nothing if the contact does not exist.

        Args:
            phone: The contact's phone number used to identify the conversation.
        """
        contact = self._uow.contacts.get_or_create_by_phone(phone)
        conversation = self._uow.conversations.get_or_create_for_contact(contact.id)
        self._uow.messages.delete_by_conversation(conversation.id)
        self._uow.commit()
        logger.info("Cleared history for conversation %s", conversation.id)
