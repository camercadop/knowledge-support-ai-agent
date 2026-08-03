import uuid
from abc import abstractmethod

from app.application.shared.ports.repository import CrudRepository
from app.application.support.models.knowledge_base import KnowledgeBase


class AbstractKnowledgeBaseRepository(CrudRepository[KnowledgeBase]):
    """Port that defines the contract for knowledge base persistence."""

    @abstractmethod
    def create(self, name: str, description: str | None = None) -> KnowledgeBase:
        """Persist a new knowledge base and return it."""

    @abstractmethod
    def get_by_id(self, knowledge_base_id: uuid.UUID) -> KnowledgeBase | None:
        """Return the knowledge base with the given id, or None if not found."""

    @abstractmethod
    def list(self) -> list[KnowledgeBase]:
        """Return all knowledge bases."""

    @abstractmethod
    def delete(self, knowledge_base_id: uuid.UUID) -> None:
        """Delete the knowledge base."""

    @abstractmethod
    def update(self, entity: KnowledgeBase, **changes: object) -> KnowledgeBase:
        """Update the knowledge base and return the updated instance."""
