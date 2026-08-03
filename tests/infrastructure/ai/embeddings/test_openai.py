from unittest.mock import MagicMock, patch

from app.infrastructure.ai.embeddings.openai import OpenAIEmbeddingModel


def _make_model() -> OpenAIEmbeddingModel:
    model = OpenAIEmbeddingModel.__new__(OpenAIEmbeddingModel)
    model._client = MagicMock()
    return model


def _make_embedding_response(data: list[float]) -> MagicMock:
    response = MagicMock()
    embedding = MagicMock()
    embedding.embedding = data
    response.data = [embedding]
    return response


# --- model_name ---


def test_model_name_returns_configured_model() -> None:
    with patch("app.infrastructure.ai.embeddings.openai.settings") as mock_settings:
        mock_settings.embedding_model = "text-embedding-3-large"
        model = _make_model()
        assert model.model_name == "text-embedding-3-large"


# --- embed ---


def test_embed_calls_client_embeddings_create() -> None:
    with patch("app.infrastructure.ai.embeddings.openai.settings") as mock_settings:
        mock_settings.embedding_model = "text-embedding-3-small"
        mock_settings.embedding_dimensions = None
        mock_settings.embedding_encoding_format = "float"
        model = _make_model()
        model._client.embeddings.create.return_value = _make_embedding_response(
            [0.1, 0.2, 0.3]
        )
        result = model.embed("hello world")
        model._client.embeddings.create.assert_called_once()
        call_kwargs = model._client.embeddings.create.call_args.kwargs
        assert call_kwargs["model"] == "text-embedding-3-small"
        assert call_kwargs["input"] == "hello world"
        assert "dimensions" not in call_kwargs
        assert call_kwargs["encoding_format"] == "float"
        assert result == [0.1, 0.2, 0.3]


def test_embed_with_dimensions_passes_dimensions_to_api() -> None:
    with patch("app.infrastructure.ai.embeddings.openai.settings") as mock_settings:
        mock_settings.embedding_model = "text-embedding-3-small"
        mock_settings.embedding_dimensions = 256
        mock_settings.embedding_encoding_format = "float"
        model = _make_model()
        model._client.embeddings.create.return_value = _make_embedding_response(
            [0.1, 0.2]
        )
        result = model.embed("hello world")
        call_kwargs = model._client.embeddings.create.call_args.kwargs
        assert call_kwargs["dimensions"] == 256
        assert result == [0.1, 0.2]


def test_embed_without_dimensions_omits_dimensions_param() -> None:
    with patch("app.infrastructure.ai.embeddings.openai.settings") as mock_settings:
        mock_settings.embedding_model = "text-embedding-3-small"
        mock_settings.embedding_dimensions = None
        mock_settings.embedding_encoding_format = "float"
        model = _make_model()
        model._client.embeddings.create.return_value = _make_embedding_response(
            [0.1, 0.2]
        )
        result = model.embed("hello world")
        call_kwargs = model._client.embeddings.create.call_args.kwargs
        assert "dimensions" not in call_kwargs
        assert result == [0.1, 0.2]


def test_embed_with_base64_encoding_format() -> None:
    with patch("app.infrastructure.ai.embeddings.openai.settings") as mock_settings:
        mock_settings.embedding_model = "text-embedding-3-small"
        mock_settings.embedding_dimensions = None
        mock_settings.embedding_encoding_format = "base64"
        model = _make_model()
        model._client.embeddings.create.return_value = _make_embedding_response(
            [0.1, 0.2]
        )
        result = model.embed("hello world")
        call_kwargs = model._client.embeddings.create.call_args.kwargs
        assert call_kwargs["encoding_format"] == "base64"
        assert result == [0.1, 0.2]
