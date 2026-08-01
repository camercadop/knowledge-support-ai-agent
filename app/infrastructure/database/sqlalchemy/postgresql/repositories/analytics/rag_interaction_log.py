import uuid

from sqlalchemy.orm import Session

from app.application.analytics.models.rag_interaction_log import (
    RagInteractionLog as RagInteractionLogModel,
)
from app.application.analytics.ports.repositories.rag_interaction_log import (
    AbstractRagInteractionLogRepository,
)
from app.application.support.ports.vector_store import SearchResult
from app.infrastructure.database.sqlalchemy.postgresql.models.analytics.rag_interaction_log import (  # noqa: E501
    RagInteractionLog as RagInteractionLogORM,
)


def _deserialize_chunk(c: dict[str, object]) -> SearchResult:
    """Deserialize a JSONB chunk dict back into a SearchResult.

    Args:
        c: Raw dict loaded from the JSONB column.

    Returns:
        A SearchResult with typed fields.
    """
    return SearchResult(
        chunk_id=uuid.UUID(str(c["chunk_id"])),
        document_id=uuid.UUID(str(c["document_id"])),
        chunk=str(c["chunk"]),
        score=float(str(c["score"])),
        document_title=str(c.get("document_title", "")),
        source=str(c["source"]) if c.get("source") else None,
    )


class RagInteractionLogRepository(AbstractRagInteractionLogRepository):
    """Handles persistence operations for RagInteractionLog entries."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self._db = db

    def create(
        self,
        conversation_id: uuid.UUID,
        question: str,
        answer: str,
        model_used: str,
        chunks: list[SearchResult] | None,
        prompt_tokens: int | None,
        completion_tokens: int | None,
    ) -> RagInteractionLogModel:
        """Persist a new RAG interaction log entry and return it.

        Args:
            conversation_id: UUID of the conversation this turn belongs to.
            question: Raw user message text.
            answer: Assistant reply text.
            model_used: LLM model identifier used to generate the answer.
            chunks: Retrieved chunks as a list of dicts, or None.
            prompt_tokens: Number of tokens in the prompt, or None.
            completion_tokens: Number of tokens in the completion, or None.

        Returns:
            The persisted RagInteractionLog.
        """
        orm = RagInteractionLogORM(
            conversation_id=conversation_id,
            question=question,
            answer=answer,
            model_used=model_used,
            chunks=(
                [
                    {
                        "chunk_id": str(c.chunk_id),
                        "document_id": str(c.document_id),
                        "chunk": c.chunk,
                        "score": c.score,
                        "document_title": c.document_title,
                        "source": c.source,
                    }
                    for c in chunks
                ]
                if chunks
                else None
            ),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )
        self._db.add(orm)
        self._db.flush()
        return self._to_model(orm)

    def list_all(self) -> list[RagInteractionLogModel]:
        """Return all recorded RAG interaction logs.

        Returns:
            List of all RagInteractionLog entries ordered by creation time.
        """
        rows = (
            self._db.query(RagInteractionLogORM)
            .order_by(RagInteractionLogORM.created_at)
            .all()
        )
        return [self._to_model(row) for row in rows]

    def _to_model(self, orm: RagInteractionLogORM) -> RagInteractionLogModel:
        """Map an ORM instance to the application model.

        Args:
            orm: The ORM instance to map.

        Returns:
            The corresponding RagInteractionLog application model.
        """
        return RagInteractionLogModel(
            id=orm.id,
            conversation_id=orm.conversation_id,
            question=orm.question,
            answer=orm.answer,
            model_used=orm.model_used,
            chunks=(
                [_deserialize_chunk(c) for c in orm.chunks]
                if orm.chunks
                else None
            ),
            prompt_tokens=orm.prompt_tokens,
            completion_tokens=orm.completion_tokens,
            created_at=orm.created_at,
        )
