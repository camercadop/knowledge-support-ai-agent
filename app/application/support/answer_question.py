import logging

from app.application.ports.chat_model import ChatMessage, ChatModel, Role
from app.application.ports.embedding_model import EmbeddingModel
from app.application.ports.unit_of_work.messaging import MessagingUnitOfWork
from app.application.ports.vector_store import VectorStore

logger = logging.getLogger(__name__)


class AnswerQuestion:
    """Orchestrates a full chat turn: retrieval, persistence, history, and LLM call."""

    def __init__(
        self,
        uow: MessagingUnitOfWork,
        chat_model: ChatModel,
        embedding_model: EmbeddingModel,
        vector_store: VectorStore,
    ) -> None:
        """Initialize with a unit of work, chat model, embedding model, and vector store."""
        self._uow = uow
        self._chat_model = chat_model
        self._embedding_model = embedding_model
        self._vector_store = vector_store

    def handle(self, phone: str, user_message: str) -> str:
        """Process a user message and return the assistant reply.

        Embeds the user query, retrieves relevant knowledge chunks, finds or
        creates the contact and conversation, builds the full message history,
        calls the LLM with context, persists both turns, and returns the reply.
        """
        query_embedding = self._embedding_model.embed(user_message)
        results = self._vector_store.search(query_embedding)
        context: str | None = None
        if results:
            context = "\n\n".join(r.chunk for r in results)
            logger.info("Retrieved %s chunks for RAG context", len(results))

        contact = self._uow.contacts.get_or_create_by_phone(phone)
        conversation = self._uow.conversations.get_or_create_for_contact(contact.id)
        logger.info("Handling chat turn for conversation %s", conversation.id)

        history = self._uow.messages.list_by_conversation(conversation.id)
        messages = [ChatMessage(role=Role(m.role), content=m.content) for m in history]
        messages.append(ChatMessage(role=Role.USER, content=user_message))

        response = self._chat_model.generate(messages, context=context)

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
