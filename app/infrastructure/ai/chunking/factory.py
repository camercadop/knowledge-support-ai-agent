from collections.abc import Callable

from app.application.ports.chunk_strategy import ChunkStrategy
from app.config.settings import settings
from app.infrastructure.ai.chunking.fixed_size import FixedSizeChunkStrategy
from app.infrastructure.ai.chunking.markdown_aware import MarkdownAwareChunkStrategy
from app.infrastructure.ai.chunking.recursive import RecursiveChunkStrategy

_CHUNK_STRATEGIES: dict[str, Callable[[int, int], ChunkStrategy]] = {
    "fixed": FixedSizeChunkStrategy,
    "recursive": RecursiveChunkStrategy,
    "markdown": MarkdownAwareChunkStrategy,
}


def build_chunk_strategy() -> ChunkStrategy:
    """Instantiate the chunk strategy selected in settings.

    Returns:
        A ChunkStrategy configured with chunk_size and chunk_overlap from settings.

    Raises:
        ValueError: If the configured chunk_strategy name is not recognised.
    """
    strategy_cls = _CHUNK_STRATEGIES.get(settings.chunk_strategy)
    if strategy_cls is None:
        raise ValueError(f"Unknown chunk_strategy: {settings.chunk_strategy}")
    return strategy_cls(settings.chunk_size, settings.chunk_overlap)
