from sqlalchemy.orm import Session

from app.application.analytics.use_cases.export_rag_interactions import (
    ExportRagInteractions,
)
from app.application.analytics.use_cases.record_rag_interaction import (
    RecordRagInteraction,
)
from app.application.support.events.question_answered import QuestionAnswered
from app.application.support.ports.message_retention_policy import (
    MessageRetentionPolicy,
)
from app.application.support.services.chunk_retriever import ChunkRetriever
from app.application.support.services.history_optimizer import (
    ConversationHistoryOptimizer,
)
from app.application.support.use_cases.answer_question import AnswerQuestion
from app.application.support.use_cases.clear_history import ClearHistory
from app.application.support.use_cases.ingest_document import IngestDocument
from app.config.settings import settings
from app.container.base import BaseContainer
from app.infrastructure.ai.chat.openai import OpenAIChatModel
from app.infrastructure.ai.chunking.factory import build_chunk_strategy
from app.infrastructure.ai.embeddings.openai import OpenAIEmbeddingModel
from app.infrastructure.ai.prompt_builder.default import (
    DefaultPromptBuilder,
    PromptConfig,
)
from app.infrastructure.ai.tools.registry import build_tool_registry
from app.infrastructure.analytics.event_handlers import RagInteractionLogHandler
from app.infrastructure.database.sqlalchemy.postgresql.unit_of_work.analytics import (
    SqlAlchemyAnalyticsUnitOfWork,
)
from app.infrastructure.database.sqlalchemy.postgresql.unit_of_work.knowledge import (
    SqlAlchemyKnowledgeUnitOfWork,
)
from app.infrastructure.database.sqlalchemy.postgresql.unit_of_work.messaging import (
    SqlAlchemyMessagingUnitOfWork,
)
from app.infrastructure.events.in_memory_event_bus import InMemoryEventBus
from app.infrastructure.observability.definitions.support import (
    ANSWER_QUESTION_INSTRUMENTATION,
    INGEST_DOCUMENT_INSTRUMENTATION,
)
from app.infrastructure.observability.instrumentation import InstrumentationConfig
from app.infrastructure.vectorstores.pgvector.store import PgVectorStore


class SupportContainer(BaseContainer):
    """Lazy provider for all support use cases.

    Holds shared infrastructure singletons and builds fresh use case instances
    on every call. Nothing is instantiated until a method is called.
    """

    def _setup(self) -> None:
        self._prompt_builder = DefaultPromptBuilder(
            config=PromptConfig(
                system_instructions=settings.prompts_system_instructions,
                grounded_instructions=settings.prompts_grounded_instructions,
                no_context_instructions=settings.prompts_no_context_instructions,
            )
        )
        self._chat_model = OpenAIChatModel(prompt_builder=self._prompt_builder)
        self._chunk_strategy = build_chunk_strategy()
        self._conversation_history_optimizer = self._create_history_optimizer()

    def _create_history_optimizer(self) -> ConversationHistoryOptimizer:
        """Create the conversation history optimizer with enabled policies.

        The conversation history optimizer applies retention policies to manage
        conversation history length and composition before LLM calls. Policies
        are accumulated from configuration settings.

        Returns:
            ConversationHistoryOptimizer instance with enabled policies.
        """
        from app.infrastructure.ai.history_policies.message_count import (
            MessageCountPolicy,
        )
        from app.infrastructure.ai.history_policies.summary import (
            SummaryPolicy,
        )
        from app.infrastructure.ai.history_policies.token_limit import (
            TokenLimitPolicy,
        )

        policies: list[MessageRetentionPolicy] = [
            MessageCountPolicy(max_messages=settings.conversation_max_messages),
            TokenLimitPolicy(max_tokens=settings.conversation_max_tokens),
            SummaryPolicy(
                chat_model=self._chat_model,
                max_summary_tokens=settings.conversation_summary_max_tokens,
                max_summary_messages=settings.conversation_summary_max_messages,
            ),
        ]

        return ConversationHistoryOptimizer(policies)

    def answer_question(self, db: Session) -> AnswerQuestion:
        """Build a fresh AnswerQuestion use case bound to the given session.

        Args:
            db: Active database session for this request.

        Returns:
            A fully wired AnswerQuestion instance.
        """
        retrieval_service = ChunkRetriever(
            vector_store=PgVectorStore(db),
            top_k=settings.retrieval_top_k,
            min_score=settings.retrieval_min_score,
            max_chunks=settings.retrieval_max_chunks,
            max_context_tokens=settings.retrieval_max_context_tokens,
            encoding_name=settings.retrieval_encoding,
        )
        event_bus = InMemoryEventBus()
        event_bus.subscribe(
            QuestionAnswered,
            RagInteractionLogHandler(
                RecordRagInteraction(SqlAlchemyAnalyticsUnitOfWork(db))
            ),
        )
        return AnswerQuestion(
            uow=SqlAlchemyMessagingUnitOfWork(db),
            event_publisher=event_bus,
            chat_model=self._chat_model,
            embedding_model=self._singleton(OpenAIEmbeddingModel),
            retrieval_service=retrieval_service,
            prompt_builder=self._prompt_builder,
            instrumentation=self._instrumentation(ANSWER_QUESTION_INSTRUMENTATION),
            tool_registry=build_tool_registry(db),
        )

    def clear_history(self, db: Session) -> ClearHistory:
        """Build a fresh ClearHistory use case bound to the given session.

        Args:
            db: Active database session for this request.

        Returns:
            A fully wired ClearHistory instance.
        """
        return ClearHistory(
            uow=SqlAlchemyMessagingUnitOfWork(db),
            instrumentation=self._instrumentation(InstrumentationConfig()),
        )

    def export_rag_interactions(self, db: Session) -> ExportRagInteractions:
        """Build a fresh ExportRagInteractions use case bound to the given session.

        Args:
            db: Active database session for this request.

        Returns:
            A fully wired ExportRagInteractions instance.
        """
        return ExportRagInteractions(uow=SqlAlchemyAnalyticsUnitOfWork(db))

    def ingest_document(self, db: Session) -> IngestDocument:
        """Build a fresh IngestDocument use case bound to the given session.

        Args:
            db: Active database session for this request.

        Returns:
            A fully wired IngestDocument instance.
        """
        return IngestDocument(
            uow=SqlAlchemyKnowledgeUnitOfWork(db),
            embedding_model=self._singleton(OpenAIEmbeddingModel),
            vector_store=PgVectorStore(db),
            chunk_strategy=self._chunk_strategy,
            instrumentation=self._instrumentation(INGEST_DOCUMENT_INSTRUMENTATION),
        )
