import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.container.support import SupportContainer
from app.infrastructure.database.sqlalchemy.postgresql.engine import get_db
from app.schemas.analytics import DocumentChunk as DocumentChunkSchema
from app.schemas.analytics import RagInteractionLogResponse

router = APIRouter(prefix="/analytics")
logger = logging.getLogger(__name__)


def get_container(request: Request) -> SupportContainer:
    """Return the support container from request state.

    Args:
        request: The current FastAPI request.

    Returns:
        The SupportContainer instance stored on app.state.container.support.
    """
    container: SupportContainer = request.app.state.container.support
    return container


@router.get("/rag-interactions", response_model=list[RagInteractionLogResponse])
def list_rag_interactions(
    container: SupportContainer = Depends(get_container),
    db: Session = Depends(get_db),
) -> list[RagInteractionLogResponse]:
    """Return all recorded RAG interaction logs."""
    logger.info("Fetching all RAG interaction logs")
    logs = container.export_rag_interactions(db).handle()
    return [
        RagInteractionLogResponse(
            id=log.id,
            conversation_id=log.conversation_id,
            question=log.question,
            answer=log.answer,
            model_used=log.model_used,
            chunks=(
                [
                    DocumentChunkSchema(
                        chunk_id=c.chunk_id,
                        document_id=c.document_id,
                        score=c.score,
                    )
                    for c in log.chunks
                ]
                if log.chunks
                else None
            ),
            prompt_tokens=log.prompt_tokens,
            completion_tokens=log.completion_tokens,
            created_at=log.created_at,
        )
        for log in logs
    ]
