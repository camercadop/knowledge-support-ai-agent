import json
import logging

import boto3

from app.application.support.ports.embedding_model import (
    EmbeddingModel,
    EmbeddingModelSettings,
)
from app.infrastructure.ai.registry import llm_provider

logger = logging.getLogger(__name__)


@llm_provider("bedrock", "embedding")
class BedrockEmbeddingModel(EmbeddingModel):
    """EmbeddingModel implementation backed by the AWS Bedrock Titan Embed API."""

    @classmethod
    def build_settings(cls, settings: object) -> EmbeddingModelSettings:
        """Build EmbeddingModelSettings from application config
        for the Bedrock provider.

        Args:
            settings: The application Settings instance.

        Returns:
            An EmbeddingModelSettings instance populated from application settings.
        """
        from app.config.settings import Settings

        assert isinstance(settings, Settings)
        return EmbeddingModelSettings(
            model=settings.embedding_model,
            provider_options=settings.embedding_provider_options,
        )

    def __init__(self, settings: EmbeddingModelSettings | None) -> None:
        """Initialize the Bedrock runtime client.

        Args:
            settings: Configuration for the Bedrock embeddings client and model.
        """
        region = (
            settings.provider_options.get("region", "us-east-1")
            if settings
            else "us-east-1"
        )
        self._client = boto3.client("bedrock-runtime", region_name=region)
        self._settings = settings

    @property
    def model_name(self) -> str:
        """Return the configured embedding model identifier."""
        return self._settings.model if self._settings else ""

    def embed(self, text: str) -> list[float]:
        """Generate a vector embedding for the given text using Bedrock.

        Invokes the model configured in settings. The response body is expected
        to contain an ``embedding`` key with a list of floats, which is the
        format returned by Amazon Titan Embed and Cohere Embed models.

        Args:
            text: The input text to embed.

        Returns:
            A flat list of floats suitable for storage in a pgvector column.
        """
        if not self._settings:
            return []
        body = json.dumps({"inputText": text})
        response = self._client.invoke_model(
            modelId=self._settings.model,
            body=body,
            contentType="application/json",
            accept="application/json",
        )
        result: dict[str, list[float]] = json.loads(response["body"].read())
        logger.debug("Bedrock embedding received for model %s", self._settings.model)
        return result["embedding"]
