import logging
import uuid
from dataclasses import dataclass, field

from app.application.shared.events.event_publisher import EventPublisher
from app.application.shared.ports.unit_of_work import UnitOfWork
from app.application.shared.security.logger import log_security_event
from app.application.support.events.context_compressed import ContextCompressed
from app.application.support.events.question_answered import QuestionAnswered
from app.application.support.exceptions.message_rejected import MessageRejected
from app.application.support.ports.chat_model import (
    ChatMessage,
    ChatModel,
    ChatModelOverrides,
    ChatResponse,
    Role,
)
from app.application.support.ports.embedding_model import EmbeddingModel
from app.application.support.ports.message_sanitizer import MessageSanitizer
from app.application.support.ports.observability import BaseInstrumentation
from app.application.support.ports.prompt_builder import PromptBuilder, PromptOverrides
from app.application.support.ports.query_rewriter import QueryRewriter
from app.application.support.ports.repositories.contact import AbstractContactRepository
from app.application.support.ports.repositories.conversation import (
    AbstractConversationRepository,
)
from app.application.support.ports.repositories.message import AbstractMessageRepository
from app.application.support.ports.settings_resolver import SettingsResolver
from app.application.support.ports.tool_registry import ToolRegistry
from app.application.support.ports.vector_store import SearchResult
from app.application.support.services.chunk_retriever import (
    ChunkRetriever,
    RetrievalConfig,
    RetrievalResult,
)
from app.application.support.services.history_optimizer import (
    ConversationHistoryOptimizer,
)
from app.config.settings import settings as global_settings

logger = logging.getLogger(__name__)

_RETRIEVAL_KEYS = [
    "retrieval_top_k",
    "retrieval_min_score",
    "retrieval_max_chunks",
    "retrieval_max_context_tokens",
    "retrieval_encoding",
    "context_compression_enabled",
    "context_compression_strategy",
    "context_compression_threshold",
]

_PROMPT_KEYS = [
    "prompts_system_instructions",
    "prompts_grounded_instructions",
    "prompts_no_context_instructions",
    "prompts_message_rejected_reply",
]

_CHAT_KEYS = [
    "chat_model",
    "chat_max_tokens",
    "chat_temperature",
]


@dataclass
class GenerateOverrides:
    """Per-call overrides passed to the internal _generate method."""

    prompt: PromptOverrides | None = field(default=None)
    chat_model: ChatModelOverrides | None = field(default=None)


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
        event_publisher: Publisher used to dispatch domain events after commit.
        chat_model: LLM provider used to generate the assistant reply.
        embedding_model: Provider used to embed the user query for retrieval.
        retrieval_service: Handles vector search with post-retrieval quality controls.
        prompt_builder: Assembles the full message list including the system prompt
            and retrieved context before passing it to the chat model.
        message_sanitizer: Sanitizes user messages before they enter the prompt
            pipeline to neutralize prompt injection attempts.
        tool_registry: Optional registry of tools the model may invoke
            during generation.
        instrumentation: Observability adapter for recording spans and metrics.
        history_optimizer: Optional optimizer that applies retention policies
            to conversation history before LLM calls. When provided, the
            optimizer prunes or summarizes history before generation.
        query_rewriter: Optional rewriter that transforms the user query
            before embedding and retrieval. When provided, the rewritten
            query is used for embedding instead of the sanitized message.
    """

    def __init__(
        self,
        uow: UnitOfWork,
        event_publisher: EventPublisher,
        chat_model: ChatModel,
        embedding_model: EmbeddingModel,
        retrieval_service: ChunkRetriever,
        prompt_builder: PromptBuilder,
        message_sanitizer: MessageSanitizer,
        instrumentation: BaseInstrumentation,
        tool_registry: ToolRegistry | None = None,
        history_optimizer: ConversationHistoryOptimizer | None = None,
        query_rewriter: QueryRewriter | None = None,
        settings_resolver: SettingsResolver | None = None,
    ) -> None:
        self._uow = uow
        self._event_publisher = event_publisher
        self._chat_model = chat_model
        self._embedding_model = embedding_model
        self._retrieval_service = retrieval_service
        self._prompt_builder = prompt_builder
        self._message_sanitizer = message_sanitizer
        self._tool_registry = tool_registry
        self._instrumentation = instrumentation
        self._history_optimizer = history_optimizer
        self._query_rewriter = query_rewriter
        self._settings_resolver = settings_resolver

    def handle(
        self,
        phone: str,
        user_message: str,
        knowledge_base_id: uuid.UUID | None = None,
        metadata_filters: dict[str, str] | None = None,
    ) -> AnswerResult:
        """Process a user message and return the assistant reply with chunk metadata.

        Embeds the user query, retrieves relevant knowledge chunks, finds or
        creates the contact and conversation, builds the full message history,
        calls the LLM with context, persists both turns, and returns the reply
        alongside the search results included in the RAG context.

        Args:
            phone: The user's phone number, used to identify the contact.
            user_message: The raw message text sent by the user.
            knowledge_base_id: Optional knowledge base to scope retrieval to.
            metadata_filters: Optional key-value pairs for JSONB containment
                filtering on document metadata.

        Returns:
            AnswerResult with the assistant reply and retrieved chunk metadata.
        """
        with self._instrumentation.root_span("answer_question.handle"):
            if self._settings_resolver is not None:
                resolved = self._settings_resolver.resolve_batch(
                    _RETRIEVAL_KEYS + _PROMPT_KEYS + _CHAT_KEYS, knowledge_base_id
                )
            else:
                resolved = {
                    key: getattr(global_settings, key)
                    for key in _RETRIEVAL_KEYS + _PROMPT_KEYS + _CHAT_KEYS
                }

            try:
                sanitized_message = self._message_sanitizer.sanitize(user_message)
                rewritten_message = (
                    self._query_rewriter.rewrite(sanitized_message, history=[])
                    if self._query_rewriter is not None
                    else sanitized_message
                )
            except MessageRejected as exc:
                log_security_event(
                    "support.message_rejected", phone=phone, reason=exc.reason
                )
                return AnswerResult(
                    reply=str(resolved["prompts_message_rejected_reply"]),
                    chunks=None,
                )
            retrieval_config = RetrievalConfig(
                top_k=int(resolved["retrieval_top_k"]),  # type: ignore[call-overload]
                min_score=resolved["retrieval_min_score"],  # type: ignore[arg-type]
                max_chunks=int(resolved["retrieval_max_chunks"]),  # type: ignore[call-overload]
                max_context_tokens=int(resolved["retrieval_max_context_tokens"]),  # type: ignore[call-overload]
                encoding_name=str(resolved["retrieval_encoding"]),
                compression_enabled=bool(resolved["context_compression_enabled"]),
                compression_strategy=resolved["context_compression_strategy"],  # type: ignore[arg-type]
                compression_threshold=resolved["context_compression_threshold"],  # type: ignore[arg-type]
            )
            prompt_overrides = PromptOverrides(
                system_instructions=str(resolved["prompts_system_instructions"]),
                grounded_instructions=str(resolved["prompts_grounded_instructions"]),
                no_context_instructions=str(
                    resolved["prompts_no_context_instructions"]
                ),
            )
            chat_model_overrides = ChatModelOverrides(
                model=str(resolved["chat_model"]),
                max_tokens=int(resolved["chat_max_tokens"]),  # type: ignore[call-overload]
                temperature=float(str(resolved["chat_temperature"])),
            )

            embedding = self._embed(rewritten_message)
            retrieval = self._retrieve(
                embedding,
                query=rewritten_message,
                knowledge_base_id=knowledge_base_id,
                metadata_filters=metadata_filters,
                config=retrieval_config,
            )

            contact = self._uow.get(AbstractContactRepository).get_or_create_by_phone(  # type: ignore[type-abstract]
                phone
            )
            conversation = self._uow.get(
                AbstractConversationRepository  # type: ignore[type-abstract]
            ).get_or_create_for_contact(contact.id)
            logger.debug("Handling chat turn for conversation %s", conversation.id)

            if retrieval.compression_ratio is not None:
                self._event_publisher.publish(
                    ContextCompressed(
                        conversation_id=conversation.id,
                        strategy=str(retrieval_config.compression_strategy),
                        compression_ratio=retrieval.compression_ratio,
                        original_chunk_count=retrieval.original_chunk_count or 0,
                        compressed_chunk_count=len(retrieval.chunks),
                    )
                )

            history = self._uow.get(AbstractMessageRepository).list_by_conversation(  # type: ignore[type-abstract]
                conversation.id
            )
            messages = [
                ChatMessage(role=Role(m.role), content=m.content) for m in history
            ]
            messages.append(ChatMessage(role=Role.USER, content=rewritten_message))

            if self._history_optimizer is not None:
                messages = self._history_optimizer.optimize_history(messages)

            response = self._generate(
                messages,
                retrieval,
                overrides=GenerateOverrides(
                    prompt=prompt_overrides,
                    chat_model=chat_model_overrides,
                ),
            )
            self._record_metrics(retrieval, response)

            self._uow.get(AbstractMessageRepository).create(  # type: ignore[type-abstract]
                conversation.id, "user", user_message
            )
            self._uow.get(AbstractMessageRepository).create(  # type: ignore[type-abstract]
                conversation.id,
                "assistant",
                response.message.content,
                response.usage.total,
            )
            self._uow.commit()

            self._event_publisher.publish(
                QuestionAnswered(
                    conversation_id=conversation.id,
                    question=user_message,
                    answer=response.message.content,
                    model_used=response.model_used,
                    chunks=retrieval.chunks or None,
                    prompt_tokens=response.usage.input_tokens,
                    completion_tokens=response.usage.output_tokens,
                )
            )
            logger.debug("Chat turn complete for conversation %s", conversation.id)

            return AnswerResult(
                reply=response.message.content,
                chunks=retrieval.chunks or None,
            )

    def _embed(self, user_message: str) -> list[float]:
        """Embed the user message and record embedding latency.

        Args:
            user_message: The raw message text sent by the user.

        Returns:
            Query embedding vector.
        """
        with self._instrumentation.span("embedding.embed"):
            return self._embedding_model.embed(user_message)

    def _retrieve(
        self,
        embedding: list[float],
        config: RetrievalConfig,
        query: str | None = None,
        knowledge_base_id: uuid.UUID | None = None,
        metadata_filters: dict[str, str] | None = None,
    ) -> RetrievalResult:
        """Retrieve relevant chunks and record retrieval latency.

        Args:
            embedding: Query vector to search against.
            config: Retrieval parameters controlling filtering and token budget.
            query: Raw query text forwarded to the retrieval service for
                hybrid search implementations.
            knowledge_base_id: If set, only return chunks belonging to this
                knowledge base.
            metadata_filters: Optional key-value pairs for JSONB containment
                filtering on document metadata.

        Returns:
            RetrievalResult with context string and matched chunks.
        """
        with self._instrumentation.span("retrieval.retrieve"):
            return self._retrieval_service.retrieve(
                embedding,
                config=config,
                query=query,
                knowledge_base_id=knowledge_base_id,
                metadata_filters=metadata_filters,
            )

    def _generate(
        self,
        messages: list[ChatMessage],
        retrieval: RetrievalResult,
        overrides: GenerateOverrides,
    ) -> ChatResponse:
        """Build the prompt, call the LLM, and record generation latency.

        Args:
            messages: Full message history including the current user turn.
            retrieval: Retrieval result used to assemble the RAG context.
            overrides: Per-call prompt and chat model overrides.

        Returns:
            ChatResponse with the assistant reply and token usage.
        """
        prompt = self._prompt_builder.build(
            messages, retrieval.context, overrides.prompt
        )
        with self._instrumentation.span("llm.generate"):
            return self._chat_model.generate(
                prompt,
                tool_registry=self._tool_registry,
                overrides=overrides.chat_model,
            )

    def _record_metrics(
        self, retrieval: RetrievalResult, response: ChatResponse
    ) -> None:
        """Record per-turn RAG and token metrics.

        Args:
            retrieval: Retrieval result containing the chunks used in context.
            response: LLM response containing token usage.
        """
        chunk_count = len(retrieval.chunks)
        self._instrumentation.record_metrics(
            {
                "rag.chunk_count": chunk_count,
                "rag.avg_similarity_score": (
                    sum(r.score for r in retrieval.chunks) / chunk_count
                    if chunk_count
                    else 0.0
                ),
                "llm.input_tokens": response.usage.input_tokens,
                "llm.output_tokens": response.usage.output_tokens,
                "llm.total_tokens": response.usage.total,
            }
        )
