import logging
import math

import tiktoken

from app.application.support.ports.context_compressor import (
    CompressionResult,
    ContextCompressor,
)
from app.application.support.ports.embedding_model import EmbeddingModel
from app.application.support.ports.vector_store import SearchResult

logger = logging.getLogger(__name__)


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Return the cosine similarity between two vectors."""
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class MMRCompressor(ContextCompressor):
    """Compresses context using Maximal Marginal Relevance (MMR).

    Selects chunks that balance relevance to the query against diversity from
    already-selected chunks. A ``threshold`` (lambda in [0, 1]) controls the
    trade-off: 0.0 favors maximum diversity, 1.0 favors maximum relevance.

    Args:
        embedding_model: Provider used to embed chunks and the query for
            similarity scoring.
        encoding_name: tiktoken encoding name used for token counting.
    """

    def __init__(self, embedding_model: EmbeddingModel, encoding_name: str) -> None:
        self._embedding_model = embedding_model
        self._encoding_name = encoding_name

    @property
    def name(self) -> str:
        """Return the compression strategy identifier."""
        return "mmr"

    def compress(
        self,
        chunks: list[SearchResult],
        query: str | None = None,
        max_tokens: int | None = None,
        threshold: float | None = None,
    ) -> CompressionResult:
        """Select chunks via MMR until the token budget is exhausted.

        Args:
            chunks: Ordered list of search results to compress.
            query: Query text used to compute relevance scores. When None,
                relevance falls back to the chunk's retrieval score.
            max_tokens: Hard token limit for the compressed output. When None,
                all chunks are selected subject to MMR ordering.
            threshold: MMR lambda in [0, 1]. Defaults to 0.5.

        Returns:
            CompressionResult with the compressed chunks and compression ratio.
        """
        if not chunks:
            return CompressionResult(compressed_chunks=[], compression_ratio=0.0)

        lambda_ = threshold if threshold is not None else 0.5

        encoding = tiktoken.get_encoding(self._encoding_name)
        total_original = sum(
            len(encoding.encode(f"{r.document_title}: {r.chunk}")) for r in chunks
        )

        chunk_embeddings = [self._embedding_model.embed(r.chunk) for r in chunks]
        query_embedding = self._embedding_model.embed(query) if query else None

        def relevance(i: int) -> float:
            if query_embedding is not None:
                return _cosine_similarity(query_embedding, chunk_embeddings[i])
            return chunks[i].score

        selected: list[SearchResult] = []
        selected_idx: set[int] = set()
        used_tokens = 0

        while len(selected) < len(chunks):
            best_idx = -1
            best_score = -math.inf
            for i in range(len(chunks)):
                if i in selected_idx:
                    continue
                rel = relevance(i)
                max_sim = (
                    max(
                        (_cosine_similarity(chunk_embeddings[i], chunk_embeddings[j]))
                        for j in selected_idx
                    )
                    if selected_idx
                    else 0.0
                )
                mmr = lambda_ * rel - (1.0 - lambda_) * max_sim
                if mmr > best_score:
                    best_score = mmr
                    best_idx = i

            if best_idx == -1:
                break

            formatted = f"{chunks[best_idx].document_title}: {chunks[best_idx].chunk}"
            tokens = len(encoding.encode(formatted))
            if max_tokens is not None and used_tokens + tokens > max_tokens:
                break

            selected.append(chunks[best_idx])
            selected_idx.add(best_idx)
            used_tokens += tokens

        ratio = (used_tokens / total_original) if total_original else 0.0
        logger.debug(
            "MMRCompressor: %d/%d chunks, ratio=%.3f", len(selected), len(chunks), ratio
        )
        return CompressionResult(compressed_chunks=selected, compression_ratio=ratio)
