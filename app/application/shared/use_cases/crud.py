import uuid
from abc import ABC, abstractmethod
from typing import Any

from app.application.shared.ports.repository import CrudRepository
from app.application.shared.ports.unit_of_work import UnitOfWork


class CRUDUseCase[M](ABC):
    """Base class for CRUD use cases generic over the model type.

    Subclasses specify the model type and implement `create`.
    The `list`, `get_by_id`, `delete`, and `update` methods are inherited.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow
        self._repository = self._get_repository()

    @abstractmethod
    def _get_repository(self) -> CrudRepository[M]:
        """Return the repository bound to this use case."""

    @abstractmethod
    def create(self, *args: Any, **kwargs: Any) -> M:
        """Create a new entity."""

    def list(self) -> list[M]:
        """Return all entities."""
        return self._repository.list()

    def get_by_id(self, entity_id: uuid.UUID) -> M | None:
        """Return the entity with the given id, or None if not found."""
        return self._repository.get_by_id(entity_id)

    def delete(self, entity_id: uuid.UUID) -> None:
        """Delete the entity and commit the transaction."""
        self._repository.delete(entity_id)
        self._commit()

    def update(self, entity: M, **changes: object) -> M:
        """Update the entity and commit the transaction."""
        updated = self._repository.update(entity, **changes)
        self._commit()
        return updated

    def _commit(self) -> None:
        """Commit the current transaction."""
        self._uow.commit()
