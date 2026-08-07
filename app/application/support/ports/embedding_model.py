from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True)
class EmbeddingModelSettings:
    """Configuration for an embedding model provider.

    Shared by all EmbeddingModel implementations. Provider-specific options
    (e.g. AWS region) are passed via ``provider_options``.
    """

    model: str
    api_key: str | None = None
    base_url: str | None = None
    dimensions: int | None = None
    encoding_format: str = "float"
    provider_options: dict[str, str] = field(default_factory=dict)


class EmbeddingModel(ABC):
    """Port that defines the contract for embedding providers.

    Implementations live in infrastructure/ai/embeddings/. Use this interface
    in application-layer use cases to remain decoupled from any specific provider.
    """

    @classmethod
    def build_settings(cls, settings: object) -> EmbeddingModelSettings | None:
        """Build the settings object for this provider from application config.

        Override in concrete implementations that require configuration.
        Returns None for providers that need no settings (e.g. mock).

        Args:
            settings: The application settings object. Concrete implementations
                cast this to the expected Settings type.

        Returns:
            An EmbeddingModelSettings instance, or None.
        """
        return None

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the identifier of the embedding model."""

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Generate a vector embedding for the given text.

        Args:
            text: The input text to embed.

        Returns:
            A flat list of floats suitable for storage in a pgvector column.
        """
