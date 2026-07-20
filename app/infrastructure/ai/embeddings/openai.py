from openai import OpenAI

from app.config.settings import settings

_client = OpenAI(
    api_key=settings.openai_api_key,
    base_url=settings.openai_base_url,
)


def embed(text: str) -> list[float]:
    """Generate a vector embedding for the given text.

    Uses the model and dimensions configured in settings. Returns a flat list
    of floats suitable for storage in a pgvector column.
    """
    response = _client.embeddings.create(
        model=settings.openai_embedding_model,
        input=text,
        dimensions=settings.embedding_dimensions,
    )
    return response.data[0].embedding
