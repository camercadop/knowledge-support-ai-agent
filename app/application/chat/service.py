import logging

from sqlalchemy.orm import Session

from app.infrastructure.llm import openai_client
from app.repositories.contact import ContactRepository
from app.repositories.conversation import ConversationRepository
from app.repositories.message import MessageRepository

logger = logging.getLogger(__name__)


class ChatService:
    """Orchestrates a full chat turn: persistence, history retrieval, and LLM call."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self._contacts = ContactRepository(db)
        self._conversations = ConversationRepository(db)
        self._messages = MessageRepository(db)
        self._db = db

    def handle(self, phone: str, user_message: str) -> str:
        """Process a user message and return the assistant reply.

        Finds or creates the contact and conversation, builds the full message
        history, calls the LLM, persists both turns, and returns the reply text.
        """
        contact = self._contacts.get_or_create_by_phone(phone)
        conversation = self._conversations.get_or_create_for_contact(contact.id)
        logger.info("Handling chat turn for conversation %s", conversation.id)

        history = self._messages.list_by_conversation(conversation.id)
        messages = [{"role": m.role, "content": m.content} for m in history]
        messages.append({"role": "user", "content": user_message})

        response = openai_client.chat(messages)

        self._messages.create(conversation.id, "user", user_message)
        self._messages.create(
            conversation.id, "assistant", response.content, response.total_tokens
        )
        self._db.commit()
        logger.info("Chat turn complete for conversation %s", conversation.id)

        return response.content
