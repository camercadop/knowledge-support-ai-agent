from app.application.support.ports.embedding_model import (
    EmbeddingModel,
    EmbeddingModelSettings,
)
from app.infrastructure.ai.registry import llm_provider


@llm_provider("mock", "embedding")
class MockEmbeddingModel(EmbeddingModel):
    """Stub embedding model that returns a zero vector without making API calls.

    Use in tests to avoid real provider calls and keep the suite deterministic.
    Accepts an optional ``dimensions`` argument to control the vector length.
    """

    def __init__(
        self,
        settings: EmbeddingModelSettings | None = None,
        dimensions: int = 3,
    ) -> None:
        """Store the vector dimensions to use in embed.

        Args:
            settings: Ignored. Accepted to satisfy the EmbeddingModel contract.
            dimensions: Length of the zero vector returned by embed.
        """
        self._dimensions = dimensions

    @property
    def model_name(self) -> str:
        """Return the mock model identifier."""
        return "mock-embedding"

    def embed(self, text: str) -> list[float]:
        """Return a unit vector of the configured dimensions.

        The first element is 1.0 and the rest are 0.0, ensuring cosine distance
        is well-defined (0.0 against itself) and passes typical min_score filters.

        Args:
            text: Ignored.

        Returns:
            A unit vector with ``dimensions`` elements.
        """
        return [1.0] + [0.0] * (self._dimensions - 1)
