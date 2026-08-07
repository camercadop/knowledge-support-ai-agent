import importlib
import pkgutil
from typing import Any

from app.application.support.ports.chat_model import ChatModel
from app.application.support.ports.embedding_model import EmbeddingModel

_REGISTRY: dict[tuple[str, str], type] = {}

_CHAT_PACKAGES = [
    "app.infrastructure.ai.chat",
    "app.infrastructure.ai.mock",
]
_EMBEDDING_PACKAGES = [
    "app.infrastructure.ai.embeddings",
    "app.infrastructure.ai.mock",
]


def llm_provider(name: str, model_type: str) -> Any:
    """Register a ChatModel or EmbeddingModel class under the given
    provider name and type.

    Attach this decorator to a ChatModel or EmbeddingModel subclass to make it
    discoverable by ``get_chat_model`` and ``get_embedding_model``. Each
    (name, model_type) pair must be unique across all registered implementations.

    Args:
        name: The provider identifier (e.g. ``"openai"``, ``"bedrock"``).
        model_type: The model type, either ``"chat"`` or ``"embedding"``.

    Raises:
        ValueError: If a provider for the given (name, model_type) pair
        is already registered.

    Example:
        @llm_provider("openai", "chat")
        class OpenAIChatModel(ChatModel): ...
    """

    def decorator(cls: type) -> type:
        key = (name, model_type)
        if key in _REGISTRY:
            raise ValueError(
                f"An LLM provider for ('{name}', '{model_type}') is already registered."
            )
        _REGISTRY[key] = cls
        return cls

    return decorator


def _autodiscover(packages: list[str]) -> None:
    """Import all modules in the given packages to trigger decorator registration.

    Args:
        packages: List of dotted package paths to scan.
    """
    for package_name in packages:
        package = importlib.import_module(package_name)
        for module_info in pkgutil.iter_modules(package.__path__):
            importlib.import_module(f"{package_name}.{module_info.name}")


def get_chat_model(name: str) -> type[ChatModel]:
    """Return the ChatModel class registered for the given provider name.

    Scans chat and mock packages on first call to trigger decorator registration.

    Args:
        name: The provider identifier to look up.

    Returns:
        The ChatModel subclass registered for ``name``.

    Raises:
        KeyError: If no chat model is registered for the given name.
    """
    _autodiscover(_CHAT_PACKAGES)
    key = (name, "chat")
    if key not in _REGISTRY:
        raise KeyError(
            f"No chat model registered for provider '{name}'. "
            f"Available: {sorted(k[0] for k in _REGISTRY if k[1] == 'chat')}"
        )
    return _REGISTRY[key]


def get_embedding_model(name: str) -> type[EmbeddingModel]:
    """Return the EmbeddingModel class registered for the given provider name.

    Scans embedding and mock packages on first call to trigger decorator registration.

    Args:
        name: The provider identifier to look up.

    Returns:
        The EmbeddingModel subclass registered for ``name``.

    Raises:
        KeyError: If no embedding model is registered for the given name.
    """
    _autodiscover(_EMBEDDING_PACKAGES)
    key = (name, "embedding")
    if key not in _REGISTRY:
        raise KeyError(
            f"No embedding model registered for provider '{name}'. "
            f"Available: {sorted(k[0] for k in _REGISTRY if k[1] == 'embedding')}"
        )
    return _REGISTRY[key]
