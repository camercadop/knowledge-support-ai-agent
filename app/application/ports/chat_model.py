from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.application.ports.tool_registry import ToolRegistry


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
        self,
        messages: list[ChatMessage],
        context: str | None = None,
        tool_registry: ToolRegistry | None = None,
    ) -> ChatResponse:
        """Generate a reply for the given message history.

        Args:
            messages: Ordered list of ChatMessage value objects.
            context: Optional retrieved knowledge to inject into the system prompt.
                When provided, it is merged with the base system prompt so the model
                grounds its answer in the supplied context.
            tool_registry: Optional registry of tools the model may invoke.
                When provided, the model may call tools and receive their results
                before producing the final reply.

        Returns:
            A ChatResponse with the reply and token usage.
        """
