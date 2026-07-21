from app.application.ports.embedding_model import EmbeddingModel


class MockEmbeddingModel(EmbeddingModel):
    """Stub embedding model that returns a zero vector without making API calls.

    Use in tests to avoid real provider calls and keep the suite deterministic.
    Pass custom dimensions to match the expected vector size.
    """

    def __init__(self, dimensions: int = 3) -> None:
        """Initialize with the number of dimensions for the returned vector."""
        self._dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        """Return a zero vector of the configured dimensions.

        Args:
            text: Ignored.

        Returns:
            A list of zeros with length equal to the configured dimensions.
        """
        return [0.0] * self._dimensions
