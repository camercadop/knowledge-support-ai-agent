import logging
from dataclasses import dataclass

import tiktoken

from app.application.ports.vector_store import SearchResult, VectorStore

logger = logging.getLogger(__name__)


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


class RetrievalService:
    """Wraps vector store search with post-retrieval quality controls.

    Applies deduplication by chunk text, a max-chunks cap, and a token-based
    context size limit before returning the assembled context string.

    Args:
        vector_store: Store used to retrieve relevant knowledge chunks.
        top_k: Maximum number of results to request from the vector store.
        min_score: If set, exclude chunks with a cosine distance above this value.
        max_chunks: Maximum number of deduplicated chunks to include in context.
        max_context_tokens: Maximum total tokens allowed in the assembled context.
        encoding_name: tiktoken encoding name used for token counting.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        top_k: int,
        min_score: float | None,
        max_chunks: int,
        max_context_tokens: int,
        encoding_name: str,
    ) -> None:
        self._vector_store = vector_store
        self._top_k = top_k
        self._min_score = min_score
        self._max_chunks = max_chunks
        self._max_context_tokens = max_context_tokens
        self._encoding = tiktoken.get_encoding(encoding_name)

    def retrieve(
        self,
        embedding: list[float],
        metadata_filters: dict[str, str] | None = None,
    ) -> RetrievalResult:
        """Search the vector store and return context and chunk metadata.

        Deduplicates results by exact chunk text, caps at max_chunks, then
        truncates to max_context_tokens.

        Args:
            embedding: Query vector to search against.
            metadata_filters: Optional key-value pairs for JSONB containment filtering.

        Returns:
            RetrievalResult with the assembled context string (or None) and the
            list of SearchResult items included in context.
        """
        results = self._vector_store.search(
            embedding,
            top_k=self._top_k,
            min_score=self._min_score,
            metadata_filters=metadata_filters,
        )

        seen: set[str] = set()
        deduplicated = []
        for result in results:
            if result.chunk not in seen:
                seen.add(result.chunk)
                deduplicated.append(result)

        capped = deduplicated[: self._max_chunks]

        included: list[SearchResult] = []
        chunks: list[str] = []
        total_tokens = 0
        for result in capped:
            tokens = len(self._encoding.encode(result.chunk))
            if total_tokens + tokens > self._max_context_tokens:
                break
            chunks.append(result.chunk)
            included.append(result)
            total_tokens += tokens

        if not chunks:
            logger.info("No chunks passed retrieval filters")
            return RetrievalResult(context=None, chunks=[])

        logger.info(
            "Retrieved %s chunks (%s tokens) for RAG context", len(chunks), total_tokens
        )
        return RetrievalResult(context="\n\n".join(chunks), chunks=included)
