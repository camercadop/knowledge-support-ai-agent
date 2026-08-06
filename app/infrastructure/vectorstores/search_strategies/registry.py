import logging

from app.application.support.ports.search_strategy import SearchStrategy
from app.config.settings import Settings

logger = logging.getLogger(__name__)

_REGISTRY: dict[str, type[SearchStrategy]] = {}


def search_strategy(mode: str) -> type[SearchStrategy]:
    """Register a SearchStrategy implementation under the given mode.

    Attach this decorator to a SearchStrategy subclass to make it
    discoverable by ``get_search_strategy``. Each mode must be unique across
    all registered implementations.

    Args:
        mode: The retrieval mode identifier this implementation supports
            (e.g. ``"vector"``, ``"hybrid"``).

    Raises:
        ValueError: If a strategy for the given mode is already registered.

    Example:
        @search_strategy(mode="hybrid")
        class HybridSearchStrategy(SearchStrategy):
            def __init__(self, settings: Settings) -> None: ...
    """

    def decorator(cls: type[SearchStrategy]) -> type[SearchStrategy]:
        if mode in _REGISTRY:
            raise ValueError(
                f"A SearchStrategy for mode '{mode}' is already registered."
            )
        _REGISTRY[mode] = cls
        return cls

    return decorator  # type: ignore[return-value]


def get_search_strategy(mode: str, settings: Settings) -> SearchStrategy:
    """Instantiate the SearchStrategy registered for the given mode.

    Args:
        mode: The retrieval mode identifier to look up.
        settings: Application settings passed to the strategy constructor.

    Returns:
        An instance of the SearchStrategy registered for ``mode``.

    Raises:
        KeyError: If no strategy is registered for the given mode.
    """
    if mode not in _REGISTRY:
        raise KeyError(
            f"No SearchStrategy registered for mode '{mode}'. "
            f"Available modes: {sorted(_REGISTRY)}"
        )
    return _REGISTRY[mode](settings)  # type: ignore[call-arg]
