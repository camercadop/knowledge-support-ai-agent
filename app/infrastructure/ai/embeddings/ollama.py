from typing import Literal, cast

from openai import OpenAI

from app.application.support.ports.embedding_model import (
    EmbeddingModel,
    EmbeddingModelSettings,
)
from app.infrastructure.ai.registry import llm_provider


@llm_provider("ollama", "embedding")
class OllamaEmbeddingModel(EmbeddingModel):
    """EmbeddingModel implementation backed by the Ollama Embeddings API.

    Uses the OpenAI-compatible ``/v1/embeddings`` endpoint exposed by Ollama.
    """

    @classmethod
    def build_settings(cls, settings: object) -> EmbeddingModelSettings:
        """Build EmbeddingModelSettings from application config for the Ollama provider.

        Args:
            settings: The application Settings instance.

        Returns:
            An EmbeddingModelSettings instance populated from application settings.
        """
        from app.config.settings import Settings

        assert isinstance(settings, Settings)
        return EmbeddingModelSettings(
            model=settings.embedding_model,
            api_key=settings.embedding_api_key,
            base_url=settings.embedding_base_url,
            dimensions=settings.embedding_dimensions,
            encoding_format=settings.embedding_encoding_format,
            provider_options=settings.embedding_provider_options,
        )

    def __init__(self, settings: EmbeddingModelSettings | None) -> None:
        """Initialize the OpenAI client pointed at the Ollama endpoint.

        Args:
            settings: Configuration for the Ollama embeddings client and model.
                ``base_url`` must point to the Ollama server
                (e.g. ``http://localhost:11434/v1``).
        """
        self._client = OpenAI(
            api_key=settings.api_key if settings else "ollama",
            base_url=settings.base_url if settings else "http://localhost:11434/v1",
        )
        self._settings = settings

    @property
    def model_name(self) -> str:
        """Return the configured embedding model identifier."""
        return self._settings.model if self._settings else ""

    def embed(self, text: str) -> list[float]:
        """Generate a vector embedding for the given text using Ollama.

        Uses the model configured in settings. The ``dimensions`` parameter is
        omitted when not set, letting the model decide the output size.

        Args:
            text: The input text to embed.

        Returns:
            A flat list of floats suitable for storage in a pgvector column.
        """
        if not self._settings:
            return []
        if self._settings.dimensions:
            response = self._client.embeddings.create(
                model=self._settings.model,
                input=text,
                dimensions=self._settings.dimensions,
                encoding_format=cast(
                    Literal["float", "base64"], self._settings.encoding_format
                ),
            )
        else:
            response = self._client.embeddings.create(
                model=self._settings.model,
                input=text,
                encoding_format=cast(
                    Literal["float", "base64"], self._settings.encoding_format
                ),
            )
        return response.data[0].embedding
