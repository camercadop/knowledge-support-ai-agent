import abc
from typing import Any


class BaseInstrumentation(abc.ABC):
    """Port for recording observability data in use cases.

    Provides a uniform interface for tracing and metrics without coupling the
    application layer to any specific observability backend. Implement this in
    infrastructure and inject it into use cases.
    """

    @abc.abstractmethod
    def root_span(self, name: str) -> Any:
        """Return a context manager wrapping the operation in a root span.

        Args:
            name: Name for the root span.

        Returns:
            A context manager that opens and closes the root trace span.
        """

    @abc.abstractmethod
    def span(self, name: str) -> Any:
        """Return a context manager that times a named operation.

        Args:
            name: Identifier for the operation being timed.

        Returns:
            A context manager that records the operation duration on exit.
        """

    @abc.abstractmethod
    def record_metrics(self, data: dict[str, Any]) -> None:
        """Record arbitrary key-value metrics for the current operation.

        Args:
            data: Mapping of metric names to their values.
        """
