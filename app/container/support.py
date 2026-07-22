from sqlalchemy.orm import Session

from app.application.support.answer_question import AnswerQuestion
from app.application.support.clear_history import ClearHistory
from app.application.support.ingest_document import IngestDocument
from app.infrastructure.ai.chat.openai import OpenAIChatModel
from app.infrastructure.ai.chunking.factory import build_chunk_strategy
from app.infrastructure.ai.embeddings.openai import OpenAIEmbeddingModel
from app.infrastructure.ai.tools.registry import build_tool_registry
from app.infrastructure.database.sqlalchemy.postgresql.unit_of_work.knowledge import (
    SqlAlchemyKnowledgeUnitOfWork,
)
from app.infrastructure.database.sqlalchemy.postgresql.unit_of_work.messaging import (
    SqlAlchemyMessagingUnitOfWork,
)
from app.infrastructure.vectorstores.pgvector.store import PgVectorStore


class SupportContainer:
    """Lazy provider for all support use cases.

    Holds shared infrastructure singletons and builds fresh use case instances
    on every call. Nothing is instantiated until a method is called.
    """

    def __init__(self) -> None:
        self._chat_model = OpenAIChatModel()
        self._embedding_model = OpenAIEmbeddingModel()
        self._chunk_strategy = build_chunk_strategy()

    def answer_question(self, db: Session) -> AnswerQuestion:
        """Build a fresh AnswerQuestion use case bound to the given session.

        Args:
            db: Active database session for this request.

        Returns:
            A fully wired AnswerQuestion instance.
        """
        return AnswerQuestion(
            uow=SqlAlchemyMessagingUnitOfWork(db),
            chat_model=self._chat_model,
            embedding_model=self._embedding_model,
            vector_store=PgVectorStore(db),
            tool_registry=build_tool_registry(db),
        )

    def clear_history(self, db: Session) -> ClearHistory:
        """Build a fresh ClearHistory use case bound to the given session.

        Args:
            db: Active database session for this request.

        Returns:
            A fully wired ClearHistory instance.
        """
        return ClearHistory(uow=SqlAlchemyMessagingUnitOfWork(db))

    def ingest_document(self, db: Session) -> IngestDocument:
        """Build a fresh IngestDocument use case bound to the given session.

        Args:
            db: Active database session for this request.

        Returns:
            A fully wired IngestDocument instance.
        """
        return IngestDocument(
            uow=SqlAlchemyKnowledgeUnitOfWork(db),
            embedding_model=self._embedding_model,
            vector_store=PgVectorStore(db),
            chunk_strategy=self._chunk_strategy,
        )
