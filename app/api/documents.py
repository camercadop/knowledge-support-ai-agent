import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.container.support import SupportContainer
from app.infrastructure.database.sqlalchemy.postgresql.engine import get_db
from app.schemas.documents import DocumentIngestRequest, DocumentIngestResponse

router = APIRouter()
logger = logging.getLogger(__name__)


def get_container(request: Request) -> SupportContainer:
    """Return the support container from request state.

    Args:
        request: The current FastAPI request.

    Returns:
        The SupportContainer instance stored on app.state at startup.
    """
    container: SupportContainer = request.app.state.container.support
    return container


@router.post("/documents", response_model=DocumentIngestResponse)
def ingest_document(
    request: DocumentIngestRequest,
    container: SupportContainer = Depends(get_container),
    db: Session = Depends(get_db),
) -> DocumentIngestResponse:
    """Ingest a document into the knowledge base.

    Chunks the content, generates embeddings, and indexes them for similarity search.
    """
    safe_title = request.title.replace("\n", " ").replace("\r", " ")
    logger.info("Received ingest request for document '%s'", safe_title)
    document = container.ingest_document(db).handle(
        title=request.title,
        source=request.source,
        content=request.content,
    )
    logger.info("Document %s ingested successfully", document.id)
    return DocumentIngestResponse(
        id=document.id, title=document.title, source=document.source
    )
