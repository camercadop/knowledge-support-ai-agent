import logging
from collections.abc import Callable

from app.application.support.models.document import Document
from app.application.support.ports.chunk_strategy import ChunkStrategy
from app.application.support.ports.embedding_model import EmbeddingModel
from app.application.support.ports.observability import BaseInstrumentation
from app.application.support.ports.unit_of_work.knowledge import KnowledgeUnitOfWork
from app.application.support.ports.vector_store import VectorStore

logger = logging.getLogger(__name__)


class IngestDocument:
    """Handles document ingestion: persistence, chunking, embedding, and indexing.

    Args:
        uow: Transactional boundary for documents and document chunks.
        embedding_model: Provider used to embed each text chunk.
        vector_store: Store used to index chunk embeddings for similarity search.
        chunk_strategy: Strategy used to split document content into chunks.
        instrumentation: Observability adapter for recording spans and metrics.
    """

    def __init__(
        self,
        uow: KnowledgeUnitOfWork,
        embedding_model: EmbeddingModel,
        vector_store: VectorStore,
        chunk_strategy: ChunkStrategy,
        instrumentation: BaseInstrumentation,
    ) -> None:
        self._uow = uow
        self._embedding_model = embedding_model
        self._vector_store = vector_store
        self._chunk_strategy = chunk_strategy
        self._instrumentation = instrumentation

    def handle(
        self,
        title: str,
        source: str | None,
        content: str,
        on_chunk: Callable[[int, int], None] | None = None,
    ) -> Document:
        """Ingest a document by persisting it, chunking, embedding, and indexing.

        If a document with the same title and source already exists, it is deleted
        and replaced. Commits the transaction once at the end.

        Args:
            title: Human-readable title of the document.
            source: Optional origin of the document (e.g. file path, URL).
            content: Full raw text content of the document.
            on_chunk: Optional callback invoked after each chunk is embedded and
                indexed. Receives (current, total) chunk counts, useful for
                reporting progress to a CLI or UI.

        Returns:
            The persisted Document with chunk_count populated.
        """
        with self._instrumentation.root_span("ingest_document.handle"):
            existing = self._uow.documents.get_by_title_and_source(title, source)
            if existing is not None:
                logger.info("Replacing existing document id=%s", existing.id)
                self._uow.documents.delete(existing.id)

            logger.debug("Persisting document title=%r source=%r", title, source)
            document = self._uow.documents.create(
                title=title, source=source, content=content
            )
            logger.info("Persisted document id=%s", document.id)

            chunks = self._chunk_strategy.chunk(content)
            chunk_count = len(chunks)
            logger.debug("Chunked document id=%s chunks=%d", document.id, chunk_count)

            for i, chunk_text in enumerate(chunks, start=1):
                logger.debug(
                    "Embedding chunk %d/%d document_id=%s", i, chunk_count, document.id
                )
                with self._instrumentation.span("ingest.embedding.embed"):
                    embedding = self._embedding_model.embed(chunk_text)
                chunk = self._uow.document_chunks.create(
                    document_id=document.id,
                    chunk=chunk_text,
                    embedding=embedding,
                )
                if on_chunk is not None:
                    on_chunk(i, chunk_count)
                logger.debug("Indexing chunk %d/%d chunk_id=%s", i, chunk_count, chunk.id)
                self._vector_store.upsert(
                    chunk_id=chunk.id,
                    document_id=document.id,
                    chunk=chunk_text,
                    embedding=embedding,
                )

            self._instrumentation.record_metrics(
                {
                    "ingest.chunk_count": chunk_count,
                    "ingest.total_chunks_embedded": chunk_count,
                }
            )

            self._uow.commit()
            logger.info("Ingested document id=%s chunks=%d", document.id, chunk_count)
            return Document(
                id=document.id,
                title=document.title,
                source=document.source,
                content=document.content,
                chunk_count=chunk_count,
            )
