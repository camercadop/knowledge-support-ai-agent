from collections.abc import Callable
from typing import Any, cast

from app.infrastructure.observability.instrumentation import (
    InstrumentationConfig,
    OtelDefaultInstrumentation,
)


class BaseContainer:
    """Base class for all DI containers.

    Provides a generic singleton cache so subclasses can lazily instantiate
    and reuse dependencies without repeating the caching pattern. Use stable
    callables (classes or named methods) as factory keys — lambdas are not
    supported as they produce a new key on every call and will never cache.
    """

    def __init__(self) -> None:
        self._cache: dict[Any, Any] = {}
        self._setup()

    def _setup(self) -> None:
        """Override in subclasses to initialize instance attributes.

        Called by BaseContainer.__init__ after the cache is initialized.
        Subclasses must override this instead of defining __init__ to ensure
        _cache is always available before any _singleton or _instrumentation call.
        """

    def _singleton[T](self, factory: Callable[[], T]) -> T:
        """Return a cached instance for the given factory, creating it on first call.

        Args:
            factory: A no-argument callable that produces the dependency.

        Returns:
            The cached instance produced by factory.
        """
        if factory not in self._cache:
            self._cache[factory] = factory()
        return cast(T, self._cache[factory])

    def _instrumentation(
        self, config: InstrumentationConfig
    ) -> OtelDefaultInstrumentation:
        """Return a cached OtelDefaultInstrumentation for the given config.

        Args:
            config: InstrumentationConfig declaring timed spans and metrics.

        Returns:
            A cached OtelDefaultInstrumentation instance keyed by config.
        """
        key = ("instrumentation", config)
        if key not in self._cache:
            self._cache[key] = OtelDefaultInstrumentation(config=config)
        return cast(OtelDefaultInstrumentation, self._cache[key])
