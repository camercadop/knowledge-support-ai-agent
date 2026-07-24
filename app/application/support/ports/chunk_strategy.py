from abc import ABC, abstractmethod


class ChunkStrategy(ABC):
    """Port that defines the contract for text chunking strategies.

    Implementations live in infrastructure/ai/chunking/. Use this interface
    in application-layer use cases to remain decoupled from any specific strategy.
    """

    @abstractmethod
    def chunk(self, text: str) -> list[str]:
        """Split text into a list of chunks suitable for embedding.

        Args:
            text: The full document text to split.

        Returns:
            Ordered list of text chunks. Must not return empty strings.
        """
