from typing import TYPE_CHECKING

from app.application.support.ports.chat_model import (
    ChatMessage,
    ChatModel,
    ChatModelOverrides,
    ChatResponse,
    Role,
    TokenUsage,
)

if TYPE_CHECKING:
    from app.application.support.ports.tool_registry import ToolRegistry


class MockChatModel(ChatModel):
    """Stub chat model that returns a fixed reply without making API calls.

    Use in tests to avoid real provider calls and keep the suite deterministic.
    Pass a custom reply to control the returned content.
    """

    def __init__(
        self,
        reply: str = "mock reply",
        token_total: int = 0,
        model_used: str = "mock-model",
    ) -> None:
        """Initialize with the fixed reply, token total, and model name.

        Args:
            reply: The fixed reply text to return.
            token_total: The token total to report in usage.
            model_used: The model name to report in the response.
        """
        self._reply = reply
        self._token_total = token_total
        self._model_used = model_used

    def generate(
        self,
        messages: list[ChatMessage],
        tool_registry: ToolRegistry | None = None,
        overrides: ChatModelOverrides | None = None,
    ) -> ChatResponse:
        """Return a fixed assistant reply regardless of input.

        Args:
            messages: Ignored.
            tool_registry: Ignored.
            overrides: Ignored.

        Returns:
            A ChatResponse with the configured reply and zero token usage.
        """
        return ChatResponse(
            message=ChatMessage(role=Role.ASSISTANT, content=self._reply),
            usage=TokenUsage(total=self._token_total),
            model_used=self._model_used,
        )
