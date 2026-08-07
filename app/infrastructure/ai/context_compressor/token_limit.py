import logging

import tiktoken

from app.application.support.ports.context_compressor import (
    CompressionResult,
    ContextCompressor,
)
from app.application.support.ports.vector_store import SearchResult

logger = logging.getLogger(__name__)


class TokenLimitCompressor(ContextCompressor):
    """Compresses context by truncating to a token budget.

    Keeps the highest-ranked chunks (by original order, which reflects
    retrieval relevance) until the token budget is exhausted. This is the
    default, relevance-preserving strategy.

    Args:
        encoding_name: tiktoken encoding name used for token counting.
    """

    def __init__(self, encoding_name: str) -> None:
        self._encoding_name = encoding_name

    @property
    def name(self) -> str:
        """Return the compression strategy identifier."""
        return "token_limit"

    def compress(
        self,
        chunks: list[SearchResult],
        query: str | None = None,
        max_tokens: int | None = None,
        threshold: float | None = None,
    ) -> CompressionResult:
        """Truncate chunks to fit within the token budget.

        Args:
            chunks: Ordered list of search results to compress.
            query: Unused by this strategy.
            max_tokens: Hard token limit for the compressed output. When None,
                no compression is performed.
            threshold: Unused by this strategy.

        Returns:
            CompressionResult with the compressed chunks and compression ratio.
        """
        if not chunks:
            return CompressionResult(compressed_chunks=[], compression_ratio=0.0)

        if max_tokens is None:
            return CompressionResult(
                compressed_chunks=list(chunks), compression_ratio=1.0
            )

        encoding = tiktoken.get_encoding(self._encoding_name)
        total_original = sum(
            len(encoding.encode(f"{r.document_title}: {r.chunk}")) for r in chunks
        )

        selected: list[SearchResult] = []
        used_tokens = 0
        for result in chunks:
            formatted = f"{result.document_title}: {result.chunk}"
            tokens = len(encoding.encode(formatted))
            if used_tokens + tokens > max_tokens:
                break
            selected.append(result)
            used_tokens += tokens

        ratio = (used_tokens / total_original) if total_original else 0.0
        logger.debug(
            "TokenLimitCompressor: %d/%d chunks, ratio=%.3f",
            len(selected),
            len(chunks),
            ratio,
        )
        return CompressionResult(compressed_chunks=selected, compression_ratio=ratio)
