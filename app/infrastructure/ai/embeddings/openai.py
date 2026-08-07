from typing import Literal, cast

from openai import OpenAI

from app.application.support.ports.embedding_model import (
    EmbeddingModel,
    EmbeddingModelSettings,
)
from app.config.settings import settings
from app.infrastructure.ai.registry import llm_provider


@llm_provider("openai", "embedding")
class OpenAIEmbeddingModel(EmbeddingModel):
    """EmbeddingModel implementation backed by the OpenAI Embeddings API."""

    @classmethod
    def build_settings(cls, app_settings: object) -> EmbeddingModelSettings:
        """Build EmbeddingModelSettings from application config for the OpenAI provider.

        Args:
            app_settings: The application Settings instance.

        Returns:
            An EmbeddingModelSettings instance populated from application settings.
        """
        from app.config.settings import Settings

        assert isinstance(app_settings, Settings)
        return EmbeddingModelSettings(
            model=app_settings.embedding_model,
            api_key=app_settings.embedding_api_key,
            base_url=app_settings.embedding_base_url,
            dimensions=app_settings.embedding_dimensions,
            encoding_format=app_settings.embedding_encoding_format,
            provider_options=app_settings.embedding_provider_options,
        )

    def __init__(self) -> None:
        """Initialize the OpenAI client from the module-level settings."""
        self._client = OpenAI(
            api_key=settings.embedding_api_key,
            base_url=settings.embedding_base_url,
        )

    @property
    def model_name(self) -> str:
        """Return the configured embedding model identifier."""
        return settings.embedding_model

    def embed(self, text: str) -> list[float]:
        """Generate a vector embedding for the given text.

        Uses the model and dimensions configured in settings. Returns a flat list
        of floats suitable for storage in a pgvector column.
        """
        if settings.embedding_dimensions:
            response = self._client.embeddings.create(
                model=settings.embedding_model,
                input=text,
                dimensions=settings.embedding_dimensions,
                encoding_format=cast(
                    Literal["float", "base64"], settings.embedding_encoding_format
                ),
            )
        else:
            response = self._client.embeddings.create(
                model=settings.embedding_model,
                input=text,
                encoding_format=cast(
                    Literal["float", "base64"], settings.embedding_encoding_format
                ),
            )
        return response.data[0].embedding
