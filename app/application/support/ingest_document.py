import logging

from app.application.models.document import Document
from app.application.ports.embedding_model import EmbeddingModel
from app.application.ports.unit_of_work.knowledge import KnowledgeUnitOfWork
from app.application.ports.vector_store import VectorStore

logger = logging.getLogger(__name__)

_CHUNK_SIZE = 500
_CHUNK_OVERLAP = 50


def _chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks of fixed character size.

    Args:
        text: The full document text to split.

    Returns:
        List of text chunks.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + _CHUNK_SIZE
        chunks.append(text[start:end])
        start += _CHUNK_SIZE - _CHUNK_OVERLAP
    return chunks


class IngestDocument:
    """Handles document ingestion: persistence, chunking, embedding, and indexing."""

    def __init__(
        self,
        uow: KnowledgeUnitOfWork,
        embedding_model: EmbeddingModel,
        vector_store: VectorStore,
    ) -> None:
        """Initialize with a unit of work, embedding model, and vector store."""
        self._uow = uow
        self._embedding_model = embedding_model
        self._vector_store = vector_store

    def handle(self, title: str, source: str | None, content: str) -> Document:
        """Ingest a document by persisting it, chunking the content, and indexing
        embeddings.

        Persists the document and all its chunks, then upserts each chunk into
        the vector store. Commits the transaction once at the end.

        Args:
            title: Human-readable title of the document.
            source: Optional origin of the document (e.g. file path, URL).
            content: Full raw text content of the document.

        Returns:
            The persisted Document application model.
        """
        document = self._uow.documents.create(
            title=title, source=source, content=content
        )
        logger.info(
            "Persisted document %s (%s chunks expected)",
            document.id,
            len(content) // _CHUNK_SIZE,
        )

        chunks = _chunk_text(content)
        for chunk_text in chunks:
            embedding = self._embedding_model.embed(chunk_text)
            chunk = self._uow.document_chunks.create(
                document_id=document.id,
                chunk=chunk_text,
                embedding=embedding,
            )
            self._vector_store.upsert(
                chunk_id=chunk.id,
                document_id=document.id,
                chunk=chunk_text,
                embedding=embedding,
            )

        self._uow.commit()
        logger.info("Ingested document %s with %s chunks", document.id, len(chunks))
        return document
