import pytest
from unittest.mock import MagicMock

from app.application.support.ports.search_strategy import SearchStrategy
from app.infrastructure.vectorstores.search_strategies.registry import (
    _REGISTRY,
    get_search_strategy,
    search_strategy,
)
from app.infrastructure.vectorstores.search_strategies.strategies import (
    HybridSearchContext,
    HybridSearchStrategy,
    VectorSearchStrategy,
)


def _mock_settings(fts_language: str = "english", rrf_k: int = 60) -> MagicMock:
    return MagicMock(retrieval_hybrid_fts_language=fts_language, retrieval_hybrid_rrf_k=rrf_k)


def _base_ctx(**kwargs: object) -> dict[str, object]:
    return {
        "embedding": [0.1, 0.2],
        "top_k": 5,
        "min_score": None,
        "knowledge_base_id": None,
        "metadata_filters": None,
        "query": None,
        **kwargs,
    }


# --- VectorSearchStrategy ---


def test_vector_strategy_mode() -> None:
    assert VectorSearchStrategy(_mock_settings()).mode == "vector"


def test_vector_strategy_build_context_returns_base_search_context() -> None:
    ctx = VectorSearchStrategy(_mock_settings()).build_context(**_base_ctx())  # type: ignore[arg-type]
    assert ctx.embedding == [0.1, 0.2]
    assert ctx.top_k == 5
    assert ctx.query is None


def test_vector_strategy_ignores_query_in_context() -> None:
    ctx = VectorSearchStrategy(_mock_settings()).build_context(**_base_ctx(query="q"))  # type: ignore[arg-type]
    assert ctx.query == "q"
    assert type(ctx).__name__ == "SearchContext"


# --- HybridSearchStrategy ---


def test_hybrid_strategy_mode() -> None:
    assert HybridSearchStrategy(_mock_settings()).mode == "hybrid"


def test_hybrid_strategy_build_context_returns_hybrid_context() -> None:
    ctx = HybridSearchStrategy(_mock_settings()).build_context(**_base_ctx(query="q"))  # type: ignore[arg-type]
    assert isinstance(ctx, HybridSearchContext)
    assert ctx.query == "q"
    assert ctx.fts_language == "english"
    assert ctx.rrf_k == 60


def test_hybrid_strategy_uses_configured_fts_language() -> None:
    ctx = HybridSearchStrategy(_mock_settings(fts_language="spanish")).build_context(
        **_base_ctx(query="q")  # type: ignore[arg-type]
    )
    assert isinstance(ctx, HybridSearchContext)
    assert ctx.fts_language == "spanish"


def test_hybrid_strategy_uses_configured_rrf_k() -> None:
    ctx = HybridSearchStrategy(_mock_settings(rrf_k=30)).build_context(
        **_base_ctx(query="q")  # type: ignore[arg-type]
    )
    assert isinstance(ctx, HybridSearchContext)
    assert ctx.rrf_k == 30


def test_hybrid_strategy_build_context_with_none_query() -> None:
    ctx = HybridSearchStrategy(_mock_settings()).build_context(**_base_ctx())  # type: ignore[arg-type]
    assert isinstance(ctx, HybridSearchContext)
    assert ctx.query is None


# --- registry ---


def test_vector_mode_is_registered() -> None:
    assert "vector" in _REGISTRY


def test_hybrid_mode_is_registered() -> None:
    assert "hybrid" in _REGISTRY


def test_get_search_strategy_returns_vector_strategy() -> None:
    strategy = get_search_strategy("vector", MagicMock())
    assert isinstance(strategy, VectorSearchStrategy)


def test_get_search_strategy_returns_hybrid_strategy() -> None:
    mock_settings = MagicMock(retrieval_hybrid_fts_language="english", retrieval_hybrid_rrf_k=60)
    strategy = get_search_strategy("hybrid", mock_settings)
    assert isinstance(strategy, HybridSearchStrategy)


def test_get_search_strategy_raises_for_unknown_mode() -> None:
    with pytest.raises(KeyError):
        get_search_strategy("unknown_mode", MagicMock())


def test_search_strategy_raises_on_duplicate_mode() -> None:
    with pytest.raises(ValueError, match="already registered"):

        @search_strategy(mode="vector")
        class _Duplicate(SearchStrategy):  # type: ignore[misc]
            @property
            def mode(self) -> str:
                return "vector"

            def build_context(self, *args: object, **kwargs: object) -> object:  # type: ignore[override]
                return MagicMock()

            def execute(self, *args: object, **kwargs: object) -> object:  # type: ignore[override]
                return []
