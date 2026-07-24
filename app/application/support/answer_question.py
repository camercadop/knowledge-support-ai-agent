import logging
from dataclasses import dataclass

from opentelemetry import metrics, trace

from app.application.ports.chat_model import ChatMessage, ChatModel, ChatResponse, Role
from app.application.ports.embedding_model import EmbeddingModel
from app.application.ports.prompt_builder import PromptBuilder
from app.application.ports.tool_registry import ToolRegistry
from app.application.ports.unit_of_work.messaging import MessagingUnitOfWork
from app.application.ports.vector_store import SearchResult
from app.application.support.retrieval_service import RetrievalResult, RetrievalService
from app.infrastructure.observability.support.metrics import build_support_metrics
from app.infrastructure.observability.utils import timed_span

logger = logging.getLogger(__name__)

_tracer = trace.get_tracer(__name__)
_meter = metrics.get_meter(__name__)
_support_metrics = build_support_metrics(_meter)


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
        with _tracer.start_as_current_span("answer_question.handle") as root_span:
            embedding = self._embed(user_message)
            retrieval = self._retrieve(embedding)

            contact = self._uow.contacts.get_or_create_by_phone(phone)
            conversation = self._uow.conversations.get_or_create_for_contact(contact.id)
            logger.info("Handling chat turn for conversation %s", conversation.id)

            history = self._uow.messages.list_by_conversation(conversation.id)
            messages = [
                ChatMessage(role=Role(m.role), content=m.content) for m in history
            ]
            messages.append(ChatMessage(role=Role.USER, content=user_message))

            response = self._generate(messages, retrieval)

            self._record_span_attributes(root_span, retrieval, response)
            self._record_metrics(retrieval, response)

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

    def _embed(self, user_message: str) -> list[float]:
        """Embed the user message and record embedding latency.

        Args:
            user_message: The raw message text sent by the user.

        Returns:
            Query embedding vector.
        """
        with timed_span(
            "embedding.embed", _support_metrics.embedding_duration, _tracer
        ):
            return self._embedding_model.embed(user_message)

    def _retrieve(self, embedding: list[float]) -> RetrievalResult:
        """Retrieve relevant chunks and record retrieval latency.

        Args:
            embedding: Query vector to search against.

        Returns:
            RetrievalResult with context string and matched chunks.
        """
        with timed_span(
            "retrieval.retrieve", _support_metrics.retrieval_duration, _tracer
        ):
            return self._retrieval_service.retrieve(embedding)

    def _generate(
        self, messages: list[ChatMessage], retrieval: RetrievalResult
    ) -> ChatResponse:
        """Build the prompt, call the LLM, and record generation latency.

        Args:
            messages: Full message history including the current user turn.
            retrieval: Retrieval result used to assemble the RAG context.

        Returns:
            ChatResponse with the assistant reply and token usage.
        """
        prompt = self._prompt_builder.build(messages, retrieval.context)
        with timed_span("llm.generate", _support_metrics.llm_duration, _tracer):
            return self._chat_model.generate(prompt, tool_registry=self._tool_registry)

    def _record_span_attributes(
        self,
        span: trace.Span,
        retrieval: RetrievalResult,
        response: ChatResponse,
    ) -> None:
        """Set RAG and token attributes on the root span.

        Args:
            span: The root span for the current chat turn.
            retrieval: Retrieval result containing the chunks used in context.
            response: LLM response containing token usage.
        """
        chunk_count = len(retrieval.chunks)
        avg_score = (
            sum(r.score for r in retrieval.chunks) / chunk_count if chunk_count else 0.0
        )
        span.set_attribute("rag.chunk_count", chunk_count)
        span.set_attribute("rag.avg_similarity_score", avg_score)
        span.set_attribute("llm.input_tokens", response.usage.input_tokens or 0)
        span.set_attribute("llm.output_tokens", response.usage.output_tokens or 0)
        span.set_attribute("llm.total_tokens", response.usage.total or 0)

    def _record_metrics(
        self, retrieval: RetrievalResult, response: ChatResponse
    ) -> None:
        """Record per-turn RAG and token metrics to OTel histograms.

        Args:
            retrieval: Retrieval result containing the chunks used in context.
            response: LLM response containing token usage.
        """
        chunk_count = len(retrieval.chunks)
        avg_score = (
            sum(r.score for r in retrieval.chunks) / chunk_count if chunk_count else 0.0
        )
        _support_metrics.chunk_count.record(chunk_count)
        _support_metrics.avg_similarity_score.record(avg_score)
        if response.usage.input_tokens is not None:
            _support_metrics.input_tokens.record(response.usage.input_tokens)
        if response.usage.output_tokens is not None:
            _support_metrics.output_tokens.record(response.usage.output_tokens)
        if response.usage.total is not None:
            _support_metrics.total_tokens.record(response.usage.total)
