import logging

from app.application.ports.chat_model import ChatMessage, ChatModel, Role
from app.application.ports.unit_of_work.messaging import MessagingUnitOfWork

logger = logging.getLogger(__name__)


class AnswerQuestion:
    """Orchestrates a full chat turn: persistence, history retrieval, and LLM call."""

    def __init__(self, uow: MessagingUnitOfWork, chat_model: ChatModel) -> None:
        """Initialize with a unit of work and a chat model port."""
        self._uow = uow
        self._chat_model = chat_model

    def handle(self, phone: str, user_message: str) -> str:
        """Process a user message and return the assistant reply.

        Finds or creates the contact and conversation, builds the full message
        history, calls the LLM, persists both turns, and returns the reply text.
        """
        contact = self._uow.contacts.get_or_create_by_phone(phone)
        conversation = self._uow.conversations.get_or_create_for_contact(contact.id)
        logger.info("Handling chat turn for conversation %s", conversation.id)

        history = self._uow.messages.list_by_conversation(conversation.id)
        messages = [ChatMessage(role=Role(m.role), content=m.content) for m in history]
        messages.append(ChatMessage(role=Role.USER, content=user_message))

        response = self._chat_model.generate(messages)

        self._uow.messages.create(conversation.id, "user", user_message)
        self._uow.messages.create(
            conversation.id,
            "assistant",
            response.message.content,
            response.usage.total,
        )
        self._uow.commit()
        logger.info("Chat turn complete for conversation %s", conversation.id)

        return response.message.content
