from app.application.ports.chunk_strategy import ChunkStrategy
from app.infrastructure.ai.chunking.factory import chunk_strategy


@chunk_strategy("fixed")
class FixedSizeChunkStrategy(ChunkStrategy):
    """ChunkStrategy that splits text into overlapping fixed-character-size chunks.

    Use this strategy when document structure is unknown or irrelevant and a simple,
    predictable split is sufficient.

    Args:
        chunk_size: Maximum number of characters per chunk.
        chunk_overlap: Number of characters to overlap between consecutive chunks.
    """

    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        """Initialize with chunk size and overlap from settings."""
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def chunk(self, text: str) -> list[str]:
        """Split text into fixed-size overlapping chunks.

        Args:
            text: The full document text to split.

        Returns:
            Ordered list of non-empty text chunks.
        """
        chunks = []
        start = 0
        while start < len(text):
            end = start + self._chunk_size
            chunks.append(text[start:end])
            start += self._chunk_size - self._chunk_overlap
        return chunks
