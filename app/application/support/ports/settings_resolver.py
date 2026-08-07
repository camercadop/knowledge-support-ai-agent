import uuid
from abc import ABC, abstractmethod


class SettingsResolver(ABC):
    """Port that defines the contract for resolving settings with KB overrides.

    Implementations live in infrastructure/core/. Use this interface in
    application-layer use cases to remain decoupled from the settings
    resolution mechanism.
    """

    @abstractmethod
    def resolve_batch(
        self, keys: list[str], kb_id: uuid.UUID | None
    ) -> dict[str, object]:
        """Resolve multiple settings keys, with KB config taking priority.

        Args:
            keys: List of Settings field names to resolve.
            kb_id: The knowledge base whose config overrides are checked first.
                When None, all values are returned from the global settings.

        Returns:
            A dict mapping each key to its resolved value.
        """
