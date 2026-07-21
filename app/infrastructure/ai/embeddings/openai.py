from openai import OpenAI

from app.application.ports.embedding_model import EmbeddingModel
from app.config.settings import settings


class OpenAIEmbeddingModel(EmbeddingModel):
    """EmbeddingModel implementation backed by the OpenAI Embeddings API."""

    def __init__(self) -> None:
        """Initialize the OpenAI client from application settings."""
        self._client = OpenAI(
            api_key=settings.embedding_api_key,
            base_url=settings.embedding_base_url,
        )

    def embed(self, text: str) -> list[float]:
        """Generate a vector embedding for the given text.

        Uses the model and dimensions configured in settings. Returns a flat list
        of floats suitable for storage in a pgvector column.
        """
        response = self._client.embeddings.create(
            model=settings.embedding_model,
            input=text,
            dimensions=settings.embedding_dimensions,
        )
        return response.data[0].embedding
