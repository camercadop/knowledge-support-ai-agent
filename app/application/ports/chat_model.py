from abc import ABC, abstractmethod


class ChatModelResponse:
    """Holds the text reply and token usage from a chat model call."""

    def __init__(self, content: str, total_tokens: int | None) -> None:
        """Initialize with the reply content and token count."""
        self.content = content
        self.total_tokens = total_tokens


class ChatModel(ABC):
    """Port that defines the contract for chat completion providers.

    Implementations live in infrastructure/ai/chat/. Use this interface
    in application-layer use cases to remain decoupled from any specific provider.
    """

    @abstractmethod
    def generate(self, messages: list[dict[str, str]]) -> ChatModelResponse:
        """Generate a reply for the given message history.

        Args:
            messages: List of dicts with 'role' and 'content' keys.

        Returns:
            A ChatModelResponse with the reply text and optional token count.
        """
