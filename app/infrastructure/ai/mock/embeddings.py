from app.application.support.ports.embedding_model import EmbeddingModel


class MockEmbeddingModel(EmbeddingModel):
    """Stub embedding model that returns a unit vector without making API calls.

    Use in tests to avoid real provider calls and keep the suite deterministic.
    Pass custom dimensions to match the expected vector size.
    """

    def __init__(self, dimensions: int = 3, model_name: str = "mock-embedding") -> None:
        """Initialize with the number of dimensions for the returned vector."""
        self._dimensions = dimensions
        self._model_name = model_name

    @property
    def model_name(self) -> str:
        """Return the mock model identifier."""
        return self._model_name

    def embed(self, text: str) -> list[float]:
        """Return a unit vector of the configured dimensions.

        The first element is 1.0 and the rest are 0.0, ensuring cosine distance
        is well-defined (0.0 against itself) and passes typical min_score filters.

        Args:
            text: Ignored.

        Returns:
            A unit vector with length equal to the configured dimensions.
        """
        return [1.0] + [0.0] * (self._dimensions - 1)
