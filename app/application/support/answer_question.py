import logging
from dataclasses import dataclass

from app.application.ports.chat_model import ChatMessage, ChatModel, Role
from app.application.ports.embedding_model import EmbeddingModel
from app.application.ports.prompt_builder import PromptBuilder
from app.application.ports.tool_registry import ToolRegistry
from app.application.ports.unit_of_work.messaging import MessagingUnitOfWork
from app.application.ports.vector_store import SearchResult
from app.application.support.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AnswerResult:
    """Outcome of a single chat turn.

    Attributes:
        reply: The assistant's reply text.
        chunks: Search results included in the RAG context, or None when no
            relevant chunks were retrieved.
    """

    reply: str
    chunks: list[SearchResult] | None


class AnswerQuestion:
    """Orchestrates a full chat turn: retrieval, persistence, history, and LLM call.

    Args:
        uow: Transactional boundary for contacts, conversations, and messages.
        chat_model: LLM provider used to generate the assistant reply.
        embedding_model: Provider used to embed the user query for retrieval.
        retrieval_service: Handles vector search with post-retrieval quality controls.
        prompt_builder: Assembles the full message list including the system prompt
            and retrieved context before passing it to the chat model.
        tool_registry: Optional registry of tools the model may invoke
            during generation.
    """

    def __init__(
        self,
        uow: MessagingUnitOfWork,
        chat_model: ChatModel,
        embedding_model: EmbeddingModel,
        retrieval_service: RetrievalService,
        prompt_builder: PromptBuilder,
        tool_registry: ToolRegistry | None = None,
    ) -> None:
        self._uow = uow
        self._chat_model = chat_model
        self._embedding_model = embedding_model
        self._retrieval_service = retrieval_service
        self._prompt_builder = prompt_builder
        self._tool_registry = tool_registry

    def handle(self, phone: str, user_message: str) -> AnswerResult:
        """Process a user message and return the assistant reply with chunk metadata.

        Embeds the user query, retrieves relevant knowledge chunks, finds or
        creates the contact and conversation, builds the full message history,
        calls the LLM with context, persists both turns, and returns the reply
        alongside the search results included in the RAG context.

        Args:
            phone: The user's phone number, used to identify the contact.
            user_message: The raw message text sent by the user.

        Returns:
            AnswerResult with the assistant reply and retrieved chunk metadata.
        """
        query_embedding = self._embedding_model.embed(user_message)
        retrieval = self._retrieval_service.retrieve(query_embedding)

        contact = self._uow.contacts.get_or_create_by_phone(phone)
        conversation = self._uow.conversations.get_or_create_for_contact(contact.id)
        logger.info("Handling chat turn for conversation %s", conversation.id)

        history = self._uow.messages.list_by_conversation(conversation.id)
        messages = [ChatMessage(role=Role(m.role), content=m.content) for m in history]
        messages.append(ChatMessage(role=Role.USER, content=user_message))

        prompt = self._prompt_builder.build(messages, retrieval.context)
        response = self._chat_model.generate(prompt, tool_registry=self._tool_registry)

        self._uow.messages.create(conversation.id, "user", user_message)
        self._uow.messages.create(
            conversation.id,
            "assistant",
            response.message.content,
            response.usage.total,
        )
        self._uow.commit()
        logger.info("Chat turn complete for conversation %s", conversation.id)

        return AnswerResult(
            reply=response.message.content,
            chunks=retrieval.chunks or None,
        )
