from abc import ABC, abstractmethod


class UnitOfWork(ABC):
    """Generic unit of work port.

    Domain-specific unit of work implementations must implement this port.
    """

    @abstractmethod
    def commit(self) -> None:
        """Persist all changes made within the current transaction."""

    @abstractmethod
    def get[R](self, repo_type: type[R]) -> R:
        """Return the repository instance for the given port type.

        Implementations must look up the concrete class from the repository
        registry, instantiate it lazily, and cache it for the lifetime of
        the unit of work.

        Args:
            repo_type: The abstract repository port class to resolve.

        Returns:
            The concrete repository instance bound to the current transaction.

        Raises:
            KeyError: If no repository is registered for the given port.
        """
