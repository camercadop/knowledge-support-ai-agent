import uuid

from app.application.support.ports.search_strategy import SearchStrategy
from app.application.support.ports.vector_store import SearchResult
from app.application.support.services.chunk_retriever import (
    ChunkRetriever,
    RetrievalConfig,
)
from app.infrastructure.ai.context_compressor.token_limit import TokenLimitCompressor
from app.infrastructure.vectorstores.fake.store import FakeVectorStore


class _StubStrategy(SearchStrategy):
    @property
    def mode(self) -> str:
        return "stub"

    def build_context(self, *args, **kwargs):  # pragma: no cover - unused by pipeline
        raise NotImplementedError

    def execute(self, base_query, ctx):  # pragma: no cover - unused by pipeline
        raise NotImplementedError


def _result(chunk: str, score: float = 0.0) -> SearchResult:
    return SearchResult(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        chunk=chunk,
        score=score,
        document_title="Doc",
        source=None,
    )


def _store_with(chunks: list[str]) -> FakeVectorStore:
    store = FakeVectorStore()
    for chunk in chunks:
        store.upsert(
            chunk_id=uuid.uuid4(),
            document_id=uuid.uuid4(),
            chunk=chunk,
            embedding=[1.0, 0.0],
        )
    return store


def _config(**overrides: object) -> RetrievalConfig:
    base = {
        "top_k": 10,
        "min_score": None,
        "max_chunks": 10,
        "max_context_tokens": 100,
        "encoding_name": "cl100k_base",
    }
    base.update(overrides)
    return RetrievalConfig(**base)  # type: ignore[arg-type]


def test_retrieve_returns_context_without_compression() -> None:
    store = _store_with(["alpha", "beta"])
    retriever = ChunkRetriever(vector_store=store, strategy=_StubStrategy())
    result = retriever.retrieve(
        embedding=[1.0, 0.0], config=_config(), context_compressor=None
    )
    assert result.context is not None
    assert len(result.chunks) == 2
    assert result.compression_ratio is None
    assert result.original_chunk_count is None


def test_retrieve_applies_compression_when_enabled() -> None:
    store = _store_with(["alpha", "beta", "gamma"])
    retriever = ChunkRetriever(vector_store=store, strategy=_StubStrategy())
    compressor = TokenLimitCompressor(encoding_name="cl100k_base")
    result = retriever.retrieve(
        embedding=[1.0, 0.0],
        config=_config(compression_enabled=True, compression_strategy="token_limit"),
        context_compressor=compressor,
    )
    assert result.compression_ratio is not None
    assert result.original_chunk_count == 3
    assert len(result.chunks) <= 3


def test_compression_reduces_chunk_count_under_tight_budget() -> None:
    store = _store_with(["alpha", "beta", "gamma", "delta"])
    retriever = ChunkRetriever(vector_store=store, strategy=_StubStrategy())
    compressor = TokenLimitCompressor(encoding_name="cl100k_base")
    result = retriever.retrieve(
        embedding=[1.0, 0.0],
        config=_config(
            compression_enabled=True,
            compression_strategy="token_limit",
            max_context_tokens=3,
        ),
        context_compressor=compressor,
    )
    assert len(result.chunks) < 4
    assert result.original_chunk_count == 4
    assert result.compression_ratio is not None


def test_no_compression_when_compressor_not_supplied() -> None:
    store = _store_with(["alpha", "beta"])
    retriever = ChunkRetriever(vector_store=store, strategy=_StubStrategy())
    result = retriever.retrieve(
        embedding=[1.0, 0.0],
        config=_config(compression_enabled=True),
        context_compressor=None,
    )
    assert result.compression_ratio is None
    assert len(result.chunks) == 2


def test_deduplication_runs_before_compression() -> None:
    store = FakeVectorStore()
    for _ in range(3):
        store.upsert(
            chunk_id=uuid.uuid4(),
            document_id=uuid.uuid4(),
            chunk="duplicate",
            embedding=[1.0, 0.0],
        )
    store.upsert(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        chunk="unique",
        embedding=[1.0, 0.0],
    )
    retriever = ChunkRetriever(vector_store=store, strategy=_StubStrategy())
    compressor = TokenLimitCompressor(encoding_name="cl100k_base")
    result = retriever.retrieve(
        embedding=[1.0, 0.0],
        config=_config(compression_enabled=True, compression_strategy="token_limit"),
        context_compressor=compressor,
    )
    chunks = [c.chunk for c in result.chunks]
    assert chunks.count("duplicate") == 1
    assert "unique" in chunks


def test_empty_store_returns_none_context() -> None:
    store = FakeVectorStore()
    retriever = ChunkRetriever(vector_store=store, strategy=_StubStrategy())
    compressor = TokenLimitCompressor(encoding_name="cl100k_base")
    result = retriever.retrieve(
        embedding=[1.0, 0.0],
        config=_config(compression_enabled=True, compression_strategy="token_limit"),
        context_compressor=compressor,
    )
    assert result.context is None
    assert result.chunks == []
    assert result.compression_ratio is None
