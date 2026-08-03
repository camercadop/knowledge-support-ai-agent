import pytest

from app.application.support.ports.chunk_strategy import ChunkStrategy
from app.infrastructure.ai.chunking.factory import (
    _CHUNK_STRATEGIES,
    build_chunk_strategy,
    chunk_strategy,
)


class _FakeStrategy(ChunkStrategy):
    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str) -> list[str]:
        return [text]


def test_build_chunk_strategy_returns_instance(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(_CHUNK_STRATEGIES, "fake", _FakeStrategy)
    monkeypatch.setattr("app.infrastructure.ai.chunking.factory.settings.chunk_strategy", "fake")
    monkeypatch.setattr("app.infrastructure.ai.chunking.factory.settings.chunk_size", 100)
    monkeypatch.setattr("app.infrastructure.ai.chunking.factory.settings.chunk_overlap", 10)

    result = build_chunk_strategy()

    assert isinstance(result, _FakeStrategy)
    assert result.chunk_size == 100
    assert result.chunk_overlap == 10


def test_build_chunk_strategy_raises_for_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.infrastructure.ai.chunking.factory.settings.chunk_strategy", "unknown"
    )

    with pytest.raises(ValueError, match="Unknown chunk_strategy: unknown"):
        build_chunk_strategy()


def test_chunk_strategy_decorator_registers_class() -> None:
    @chunk_strategy("test_fake")
    class _Registered(ChunkStrategy):
        def __init__(self, chunk_size: int, chunk_overlap: int) -> None: ...

        def chunk(self, text: str) -> list[str]:
            return [text]

    assert _CHUNK_STRATEGIES["test_fake"] is _Registered
