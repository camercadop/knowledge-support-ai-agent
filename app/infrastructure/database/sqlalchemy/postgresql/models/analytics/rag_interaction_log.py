import uuid

from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.sqlalchemy.postgresql.models.analytics.base import (
    AnalyticsBase,
)


class RagInteractionLog(AnalyticsBase):
    """Records a full RAG pipeline turn for analytics and export.

    Captures the question, generated answer, retrieved chunks, model used,
    and token usage for every turn handled by AnswerQuestion.
    """

    __tablename__ = "rag_interaction_logs"
    __table_args__ = {"schema": "analytics"}

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        # FK to the conversation
        nullable=False,
    )
    question: Mapped[str] = mapped_column(
        # Raw user message text
        Text,
        nullable=False,
    )
    answer: Mapped[str] = mapped_column(
        # Assistant reply text
        Text,
        nullable=False,
    )
    model_used: Mapped[str] = mapped_column(
        # LLM model identifier used to generate the answer
        nullable=False,
    )
    chunks: Mapped[list[dict[str, object]] | None] = mapped_column(
        # Retrieved chunks as a list of {content, score, document_id} dicts
        JSONB,
        nullable=True,
    )
    prompt_tokens: Mapped[int | None] = mapped_column(
        # Number of tokens in the prompt sent to the LLM
        nullable=True,
    )
    completion_tokens: Mapped[int | None] = mapped_column(
        # Number of tokens in the LLM completion
        nullable=True,
    )
