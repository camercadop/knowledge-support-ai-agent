import logging
import uuid
from dataclasses import dataclass

import tiktoken

from app.application.support.ports.search_strategy import SearchStrategy
from app.application.support.ports.vector_store import SearchResult, VectorStore

logger = logging.getLogger(__name__)


def _format_chunk(result: SearchResult) -> str:
    """Format a search result chunk with its document title and source.

    Args:
        result: The search result containing chunk text, document title,
            and source URL.

    Returns:
        A formatted string that includes the document title and source
        alongside the chunk text for citation purposes.
    """
    if result.source:
        return f"{result.document_title} ({result.source}): {result.chunk}"
    return f"{result.document_title}: {result.chunk}"


@dataclass(frozen=True)
class RetrievalResult:
    """Outcome of a retrieval pass.

    Bundles the assembled context string with the raw search results so callers
    can access chunk metadata (ids, scores) without re-querying the store.

    Attributes:
        context: Assembled context string ready for the prompt, or None when no
            chunks passed the filters.
        chunks: Ordered list of SearchResult items that were included in context.
    """

    context: str | None
    chunks: list[SearchResult]


class ChunkRetriever:
    """Wraps vector store search with post-retrieval quality controls.

    Applies deduplication by chunk text, a max-chunks cap, and a token-based
    context size limit before returning the assembled context string.

    Args:
        vector_store: Store used to retrieve relevant knowledge chunks.
        strategy: SearchStrategy that controls retrieval mode and context
            construction.
        top_k: Maximum number of results to request from the vector store.
        min_score: If set, exclude chunks with a cosine distance above this value.
        max_chunks: Maximum number of deduplicated chunks to include in context.
        max_context_tokens: Maximum total tokens allowed in the assembled context.
        encoding_name: tiktoken encoding name used for token counting.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        strategy: SearchStrategy,
        top_k: int,
        min_score: float | None,
        max_chunks: int,
        max_context_tokens: int,
        encoding_name: str,
    ) -> None:
        self._vector_store = vector_store
        self._strategy = strategy
        self._top_k = top_k
        self._min_score = min_score
        self._max_chunks = max_chunks
        self._max_context_tokens = max_context_tokens
        self._encoding = tiktoken.get_encoding(encoding_name)

    def retrieve(
        self,
        embedding: list[float],
        query: str | None = None,
        knowledge_base_id: uuid.UUID | None = None,
        metadata_filters: dict[str, str] | None = None,
    ) -> RetrievalResult:
        """Search the vector store and return context and chunk metadata.

        Deduplicates results by exact chunk text, caps at max_chunks, then
        truncates to max_context_tokens.

        Args:
            embedding: Query vector to search against.
            query: Raw query text forwarded to the active search strategy.
            knowledge_base_id: If set, only return chunks belonging to this
                knowledge base.
            metadata_filters: Optional key-value pairs for JSONB containment filtering.

        Returns:
            RetrievalResult with the assembled context string (or None) and the
            list of SearchResult items included in context.
        """
        results = self._vector_store.search(
            embedding,
            top_k=self._top_k,
            min_score=self._min_score,
            knowledge_base_id=knowledge_base_id,
            metadata_filters=metadata_filters,
            query=query,
        )
        logger.debug("Vector search returned %d results", len(results))
        for r in results:
            logger.debug(
                "chunk score=%.4f document=%r source=%r",
                r.score,
                r.document_title,
                r.source,
            )

        seen: set[str] = set()
        deduplicated = []
        for result in results:
            if result.chunk not in seen:
                seen.add(result.chunk)
                deduplicated.append(result)

        capped = deduplicated[: self._max_chunks]
        logger.debug("%d chunks after dedup+cap", len(capped))

        included: list[SearchResult] = []
        chunks: list[str] = []
        total_tokens = 0
        for result in capped:
            formatted = _format_chunk(result)
            tokens = len(self._encoding.encode(formatted))
            if total_tokens + tokens > self._max_context_tokens:
                break
            chunks.append(formatted)
            included.append(result)
            total_tokens += tokens

        if not chunks:
            logger.debug("No chunks passed retrieval filters")
            return RetrievalResult(context=None, chunks=[])

        logger.debug(
            "Retrieved %s chunks (%s tokens) for RAG context", len(chunks), total_tokens
        )
        return RetrievalResult(context="\n\n".join(chunks), chunks=included)
