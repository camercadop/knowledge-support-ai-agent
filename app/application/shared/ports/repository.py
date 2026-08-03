import uuid
from abc import ABC, abstractmethod


class Repository(ABC):
    """Marker base class for all repository ports."""


class CrudRepository[M](Repository):
    """Generic base for repositories that follow the standard CRUD shape.

    Repositories with domain-specific access patterns extend Repository directly.
    """

    @abstractmethod
    def get_by_id(self, entity_id: uuid.UUID) -> M | None: ...

    @abstractmethod
    def list(self) -> list[M]: ...

    @abstractmethod
    def delete(self, entity_id: uuid.UUID) -> None: ...

    @abstractmethod
    def update(self, entity: M, **changes: object) -> M: ...
