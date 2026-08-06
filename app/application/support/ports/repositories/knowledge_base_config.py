import uuid
from abc import ABC, abstractmethod

from app.application.support.models.knowledge_base_config import KnowledgeBaseConfig


class AbstractKnowledgeBaseConfigRepository(ABC):
    """Port that defines the contract for knowledge base configuration persistence."""

    @abstractmethod
    def set(
        self, knowledge_base_id: uuid.UUID, key: str, value: str
    ) -> KnowledgeBaseConfig:
        """Upsert a configuration entry for the given knowledge base.

        Creates the entry if the key does not exist, or updates the value if it does.

        Args:
            knowledge_base_id: The knowledge base this entry belongs to.
            key: The configuration key.
            value: The configuration value, always stored as a string.

        Returns:
            The persisted KnowledgeBaseConfig entry.
        """

    @abstractmethod
    def get_by_knowledge_base_id(self, knowledge_base_id: uuid.UUID) -> dict[str, str]:
        """Return all configuration entries for the given knowledge base as a dict.

        Args:
            knowledge_base_id: The knowledge base to load config for.

        Returns:
            A dict mapping each key to its value. Empty dict if no entries exist.
        """

    @abstractmethod
    def delete(self, knowledge_base_id: uuid.UUID, key: str) -> None:
        """Remove a single configuration entry.

        Args:
            knowledge_base_id: The knowledge base the entry belongs to.
            key: The configuration key to remove.
        """
