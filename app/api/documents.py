import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.application.support.ingest_document import IngestDocument
from app.infrastructure.ai.embeddings.openai import OpenAIEmbeddingModel
from app.infrastructure.database.engine import get_db
from app.infrastructure.database.unit_of_work.knowledge import (
    SqlAlchemyKnowledgeUnitOfWork,
)
from app.infrastructure.vectorstores.pgvector.store import PgVectorStore
from app.schemas.documents import DocumentIngestRequest, DocumentIngestResponse

router = APIRouter()
logger = logging.getLogger(__name__)

_embedding_model = OpenAIEmbeddingModel()


@router.post("/documents", response_model=DocumentIngestResponse)
def ingest_document(
    request: DocumentIngestRequest, db: Session = Depends(get_db)
) -> DocumentIngestResponse:
    """Ingest a document into the knowledge base.

    Chunks the content, generates embeddings, and indexes them for similarity search.
    """
    logger.info("Received ingest request for document '%s'", request.title)
    use_case = IngestDocument(
        uow=SqlAlchemyKnowledgeUnitOfWork(db),
        embedding_model=_embedding_model,
        vector_store=PgVectorStore(db),
    )
    document = use_case.handle(
        title=request.title,
        source=request.source,
        content=request.content,
    )
    logger.info("Document %s ingested successfully", document.id)
    return DocumentIngestResponse(
        id=document.id, title=document.title, source=document.source
    )
