import uuid

from app.application.support.ports.vector_store import SearchResult
from app.infrastructure.ai.context_compressor.token_limit import TokenLimitCompressor


def _result(chunk: str, score: float = 1.0) -> SearchResult:
    return SearchResult(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        chunk=chunk,
        score=score,
        document_title="Doc",
        source=None,
    )


def test_returns_empty_result_for_empty_input() -> None:
    compressor = TokenLimitCompressor(encoding_name="cl100k_base")
    result = compressor.compress(chunks=[], max_tokens=100)
    assert result.compressed_chunks == []
    assert result.compression_ratio == 0.0


def test_returns_all_chunks_when_max_tokens_is_none() -> None:
    compressor = TokenLimitCompressor(encoding_name="cl100k_base")
    chunks = [_result("alpha beta"), _result("gamma delta")]
    result = compressor.compress(chunks=chunks, max_tokens=None)
    assert result.compressed_chunks == chunks
    assert result.compression_ratio == 1.0


def test_truncates_to_token_budget_keeping_highest_ranked() -> None:
    compressor = TokenLimitCompressor(encoding_name="cl100k_base")
    chunks = [_result("alpha"), _result("beta"), _result("gamma")]
    result = compressor.compress(chunks=chunks, max_tokens=3)
    assert len(result.compressed_chunks) < len(chunks)
    assert result.compressed_chunks[0].chunk == "alpha"
    assert 0.0 < result.compression_ratio <= 1.0


def test_compression_ratio_is_ratio_of_used_to_original_tokens() -> None:
    compressor = TokenLimitCompressor(encoding_name="cl100k_base")
    chunks = [_result("alpha"), _result("beta")]
    result = compressor.compress(chunks=chunks, max_tokens=3)
    assert result.compression_ratio <= 0.5


def test_truncates_to_zero_when_budget_below_single_chunk() -> None:
    compressor = TokenLimitCompressor(encoding_name="cl100k_base")
    chunks = [_result("alpha"), _result("beta")]
    result = compressor.compress(chunks=chunks, max_tokens=2)
    assert result.compressed_chunks == []
    assert result.compression_ratio == 0.0


def test_name_is_token_limit() -> None:
    compressor = TokenLimitCompressor(encoding_name="cl100k_base")
    assert compressor.name == "token_limit"
