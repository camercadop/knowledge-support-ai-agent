from abc import ABC, abstractmethod


class UnitOfWork(ABC):
    """Generic unit of work port.

    Domain-specific unit of work implementations (e.g. KnowledgeUnitOfWork,
    MessagingUnitOfWork) must implement this port.
    """

    @abstractmethod
    def commit(self) -> None:
        """Persist all changes made within the current transaction."""
