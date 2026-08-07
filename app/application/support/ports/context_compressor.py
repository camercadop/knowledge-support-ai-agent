from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.application.support.ports.vector_store import SearchResult


@dataclass(frozen=True)
class CompressionResult:
    """Outcome of a context compression pass.

    Attributes:
        compressed_chunks: The chunks after compression, in order.
        compression_ratio: Ratio of compressed tokens to original tokens (0.0-1.0).
    """

    compressed_chunks: list[SearchResult]
    compression_ratio: float


class ContextCompressor(ABC):
    """Port that defines a pluggable context compression strategy.

    Compression reduces the number of chunks (and thus tokens) in the retrieved
    context while preserving relevance and diversity. Implementations live in
    infrastructure/ai/context_compressor/.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the compression strategy identifier this compressor supports."""

    @abstractmethod
    def compress(
        self,
        chunks: list[SearchResult],
        query: str | None = None,
        max_tokens: int | None = None,
        threshold: float | None = None,
    ) -> CompressionResult:
        """Compress a list of search results to fit within token budget.

        Args:
            chunks: Ordered list of search results to compress.
            query: Original query text, used by strategies that need it (e.g., MMR).
            max_tokens: Optional hard token limit for the compressed output.
            threshold: Strategy-specific parameter (e.g., MMR lambda threshold).

        Returns:
            CompressionResult with the compressed chunks and compression ratio.
        """
