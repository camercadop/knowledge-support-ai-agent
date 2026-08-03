from collections.abc import Callable

from app.application.support.ports.chunk_strategy import ChunkStrategy
from app.config.settings import settings

_CHUNK_STRATEGIES: dict[str, Callable[[int, int], ChunkStrategy]] = {}


def chunk_strategy[C: type[ChunkStrategy]](name: str) -> Callable[[C], C]:
    """Class decorator that registers a ChunkStrategy implementation under a name.

    Apply this decorator to any ChunkStrategy subclass to make it available to
    build_chunk_strategy. The name must match the value set in CHUNK_STRATEGY
    env var.

    Args:
        name: The key used to select this strategy via settings.

    Returns:
        The unmodified class, registered as a side effect.
    """

    def decorator(cls: C) -> C:
        _CHUNK_STRATEGIES[name] = cls
        return cls

    return decorator


def build_chunk_strategy() -> ChunkStrategy:
    """Instantiate the chunk strategy selected in settings.

    Strategies must be registered via @chunk_strategy before this is called.
    Import app.infrastructure.ai.chunking to ensure all built-in strategies
    are registered.

    Returns:
        A ChunkStrategy configured with chunk_size and chunk_overlap from settings.

    Raises:
        ValueError: If the configured chunk_strategy name is not recognised.
    """
    strategy_cls = _CHUNK_STRATEGIES.get(settings.chunk_strategy)
    if strategy_cls is None:
        raise ValueError(f"Unknown chunk_strategy: {settings.chunk_strategy}")
    return strategy_cls(settings.chunk_size, settings.chunk_overlap)
