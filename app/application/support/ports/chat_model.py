from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from app.application.support.ports.tool_registry import ToolRegistry


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
    input_tokens: int | None = None
    output_tokens: int | None = None


@dataclass(frozen=True)
class ChatResponse:
    """The model's reply to a list of messages."""

    message: ChatMessage
    usage: TokenUsage
    model_used: str


class ChatModelOverrides(TypedDict, total=False):
    """Per-call chat model overrides.

    All keys are optional. Any key present takes precedence over the model's
    configured default for that option. Omitted keys fall back to the
    model's own configuration.
    """

    model: str
    max_tokens: int
    temperature: float


@dataclass(frozen=True)
class ChatModelSettings:
    """Configuration for a chat model provider.

    Shared by all ChatModel implementations. Provider-specific options
    (e.g. AWS region) are passed via ``provider_options``.
    """

    model: str
    max_tokens: int
    temperature: float
    api_key: str | None = None
    base_url: str | None = None
    provider_options: dict[str, str] = field(default_factory=dict)


class ChatModel(ABC):
    """Port that defines the contract for chat completion providers.

    Implementations live in infrastructure/ai/chat/. Use this interface
    in application-layer use cases to remain decoupled from any specific provider.
    """

    @classmethod
    def build_settings(cls, settings: object) -> ChatModelSettings | None:
        """Build the settings object for this provider from application config.

        Override in concrete implementations that require configuration.
        Returns None for providers that need no settings (e.g. mock).

        Args:
            settings: The application settings object. Concrete implementations
                cast this to the expected Settings type.

        Returns:
            A ChatModelSettings instance, or None.
        """
        return None

    @abstractmethod
    def generate(
        self,
        messages: list[ChatMessage],
        tool_registry: ToolRegistry | None = None,
        overrides: ChatModelOverrides | None = None,
    ) -> ChatResponse:
        """Generate a reply for the given message history.

        Args:
            messages: Ordered list of ChatMessage value objects. The caller is
                responsible for prepending any system message via a PromptBuilder
                before passing the list here.
            tool_registry: Optional registry of tools the model may invoke.
                When provided, the model may call tools and receive their results
                before producing the final reply.
            overrides: Optional per-call overrides for model, max_tokens, and
                temperature. Any key present takes precedence over the model's
                configured defaults.

        Returns:
            A ChatResponse with the reply and token usage.
        """
