from abc import ABC, abstractmethod


class EmbeddingModel(ABC):
    """Port that defines the contract for embedding providers.

    Implementations live in infrastructure/ai/embeddings/. Use this interface
    in application-layer use cases to remain decoupled from any specific provider.
    """

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Generate a vector embedding for the given text.

        Args:
            text: The input text to embed.

        Returns:
            A flat list of floats suitable for storage in a pgvector column.
        """
