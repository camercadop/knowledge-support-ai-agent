from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum


class Role(StrEnum):
    """Valid roles for a chat message."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    DEVELOPER = "developer"


@dataclass(frozen=True)
class ChatMessage:
    """A single message in a conversation turn."""

    role: Role
    content: str


@dataclass(frozen=True)
class TokenUsage:
    """Token consumption reported by the model."""

    total: int | None


@dataclass(frozen=True)
class ChatResponse:
    """The model's reply to a list of messages."""

    message: ChatMessage
    usage: TokenUsage


class ChatModel(ABC):
    """Port that defines the contract for chat completion providers.

    Implementations live in infrastructure/ai/chat/. Use this interface
    in application-layer use cases to remain decoupled from any specific provider.
    """

    @abstractmethod
    def generate(
        self, messages: list[ChatMessage], context: str | None = None
    ) -> ChatResponse:
        """Generate a reply for the given message history.

        Args:
            messages: Ordered list of ChatMessage value objects.
            context: Optional retrieved knowledge to inject into the system prompt.
                When provided, it is merged with the base system prompt so the model
                grounds its answer in the supplied context.

        Returns:
            A ChatResponse with the reply and token usage.
        """
