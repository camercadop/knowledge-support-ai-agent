from sqlalchemy.orm import Session

from app.application.support.answer_question import AnswerQuestion
from app.application.support.clear_history import ClearHistory
from app.application.support.ingest_document import IngestDocument
from app.infrastructure.ai.chat.openai import OpenAIChatModel
from app.infrastructure.ai.chunking.factory import build_chunk_strategy
from app.infrastructure.ai.embeddings.openai import OpenAIEmbeddingModel
from app.infrastructure.ai.tools.registry import build_tool_registry
from app.infrastructure.database.sqlalchemy.postgresql.engine import SessionLocal
from app.infrastructure.database.sqlalchemy.postgresql.unit_of_work.knowledge import (
    SqlAlchemyKnowledgeUnitOfWork,
)
from app.infrastructure.database.sqlalchemy.postgresql.unit_of_work.messaging import (
    SqlAlchemyMessagingUnitOfWork,
)
from app.infrastructure.vectorstores.pgvector.store import PgVectorStore

_chat_model = OpenAIChatModel()
_embedding_model = OpenAIEmbeddingModel()


def get_session() -> Session:
    """Return a new database session.

    The caller is responsible for closing the session after use.

    Returns:
        An active SQLAlchemy Session.
    """
    return SessionLocal()


def build_answer_question(db: Session) -> AnswerQuestion:
    """Build an AnswerQuestion use case with all required dependencies.

    Args:
        db: Active database session.

    Returns:
        A fully wired AnswerQuestion instance.
    """
    return AnswerQuestion(
        uow=SqlAlchemyMessagingUnitOfWork(db),
        chat_model=_chat_model,
        embedding_model=_embedding_model,
        vector_store=PgVectorStore(db),
        tool_registry=build_tool_registry(db),
    )


def build_clear_history(db: Session) -> ClearHistory:
    """Build a ClearHistory use case.

    Args:
        db: Active database session.

    Returns:
        A fully wired ClearHistory instance.
    """
    return ClearHistory(uow=SqlAlchemyMessagingUnitOfWork(db))


def build_ingest_document(db: Session) -> IngestDocument:
    """Build an IngestDocument use case.

    Args:
        db: Active database session.

    Returns:
        A fully wired IngestDocument instance.
    """
    return IngestDocument(
        uow=SqlAlchemyKnowledgeUnitOfWork(db),
        embedding_model=_embedding_model,
        vector_store=PgVectorStore(db),
        chunk_strategy=build_chunk_strategy(),
    )
