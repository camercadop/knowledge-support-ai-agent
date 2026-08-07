import uuid

from app.application.support.ports.embedding_model import EmbeddingModel
from app.application.support.ports.vector_store import SearchResult
from app.infrastructure.ai.context_compressor.mmr import MMRCompressor


class _FakeEmbeddingModel(EmbeddingModel):
    @property
    def model_name(self) -> str:
        return "fake"

    def embed(self, text: str) -> list[float]:
        if text == "query":
            return [1.0, 0.0]
        return [0.0, 1.0]


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
    compressor = MMRCompressor(
        embedding_model=_FakeEmbeddingModel(), encoding_name="cl100k_base"
    )
    result = compressor.compress(chunks=[], query="query", max_tokens=100)
    assert result.compressed_chunks == []
    assert result.compression_ratio == 0.0


def test_selects_only_relevant_chunk_when_budget_is_small() -> None:
    compressor = MMRCompressor(
        embedding_model=_FakeEmbeddingModel(), encoding_name="cl100k_base"
    )
    chunks = [_result("query", score=0.9), _result("unrelated", score=0.1)]
    result = compressor.compress(
        chunks=chunks, query="query", max_tokens=3, threshold=1.0
    )
    assert len(result.compressed_chunks) == 1
    assert result.compressed_chunks[0].chunk == "query"


def test_high_lambda_favors_relevance() -> None:
    compressor = MMRCompressor(
        embedding_model=_FakeEmbeddingModel(), encoding_name="cl100k_base"
    )
    chunks = [_result("query", score=0.9), _result("unrelated", score=0.1)]
    result = compressor.compress(
        chunks=chunks, query="query", max_tokens=100, threshold=1.0
    )
    assert result.compressed_chunks[0].chunk == "query"


def test_low_lambda_favors_diversity() -> None:
    compressor = MMRCompressor(
        embedding_model=_FakeEmbeddingModel(), encoding_name="cl100k_base"
    )
    chunks = [_result("query", score=0.9), _result("unrelated", score=0.1)]
    result = compressor.compress(
        chunks=chunks, query="query", max_tokens=100, threshold=0.0
    )
    assert len(result.compressed_chunks) == 2


def test_falls_back_to_chunk_score_when_query_is_none() -> None:
    compressor = MMRCompressor(
        embedding_model=_FakeEmbeddingModel(), encoding_name="cl100k_base"
    )
    chunks = [_result("a", score=0.9), _result("b", score=0.1)]
    result = compressor.compress(chunks=chunks, query=None, max_tokens=100)
    assert result.compressed_chunks[0].chunk == "a"


def test_compression_ratio_within_bounds() -> None:
    compressor = MMRCompressor(
        embedding_model=_FakeEmbeddingModel(), encoding_name="cl100k_base"
    )
    chunks = [_result("query"), _result("unrelated")]
    result = compressor.compress(
        chunks=chunks, query="query", max_tokens=2, threshold=1.0
    )
    assert 0.0 <= result.compression_ratio <= 1.0


def test_name_is_mmr() -> None:
    compressor = MMRCompressor(
        embedding_model=_FakeEmbeddingModel(), encoding_name="cl100k_base"
    )
    assert compressor.name == "mmr"
