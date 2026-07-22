from app.application.ports.chunk_strategy import ChunkStrategy

_SEPARATORS = ["\n## ", "\n### ", "\n#### ", "\n\n", "\n", ". ", " ", ""]


class MarkdownAwareChunkStrategy(ChunkStrategy):
    """ChunkStrategy that splits Markdown documents at heading boundaries first.

    Prefers splitting at heading levels (##, ###, ####) before falling back to
    paragraph and sentence boundaries. Keeps heading context together with its
    content, producing chunks that are more meaningful for RAG retrieval.

    Args:
        chunk_size: Maximum number of characters per chunk.
        chunk_overlap: Number of characters to overlap between consecutive chunks.
    """

    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        """Initialize with chunk size and overlap from settings."""
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def chunk(self, text: str) -> list[str]:
        """Split Markdown text using heading-aware separator hierarchy.

        Args:
            text: The full Markdown document text to split.

        Returns:
            Ordered list of non-empty text chunks.
        """
        return self._split(text, _SEPARATORS)

    def _split(self, text: str, separators: list[str]) -> list[str]:
        """Recursively split text using the first separator that produces
        manageable pieces.

        Falls back to the next separator when a piece still exceeds chunk_size.
        Merges small pieces with overlap to respect chunk_size.

        Args:
            text: Text to split.
            separators: Ordered list of separators to try.

        Returns:
            List of chunks within chunk_size.
        """
        if len(text) <= self._chunk_size:
            return [text]

        separator = separators[0]
        remaining = separators[1:]

        parts = text.split(separator) if separator else list(text)
        chunks: list[str] = []
        current = ""

        for part in parts:
            if current:
                candidate = (current + separator + part).lstrip(separator)
            else:
                candidate = part
            if len(candidate) <= self._chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                    overlap_start = max(0, len(current) - self._chunk_overlap)
                    tail = current[overlap_start:]
                    current = (tail + separator + part).lstrip(separator)
                if len(part) > self._chunk_size and remaining:
                    sub = self._split(part, remaining)
                    if current:
                        chunks.append(current)
                        current = ""
                    chunks.extend(sub[:-1])
                    current = sub[-1] if sub else ""
                else:
                    current = part

        if current:
            chunks.append(current)

        return [c for c in chunks if c]
