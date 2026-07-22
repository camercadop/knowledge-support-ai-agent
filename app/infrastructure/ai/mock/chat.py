from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.ports.chat_model import (
    ChatMessage,
    ChatModel,
    ChatResponse,
    Role,
    TokenUsage,
)

if TYPE_CHECKING:
    from app.application.ports.tool_registry import ToolRegistry


class MockChatModel(ChatModel):
    """Stub chat model that returns a fixed reply without making API calls.

    Use in tests to avoid real provider calls and keep the suite deterministic.
    Pass a custom reply to control the returned content.
    """

    def __init__(self, reply: str = "mock reply", token_total: int = 0) -> None:
        """Initialize with the fixed reply and token total for every generate call.

        Args:
            reply: The fixed reply text to return.
            token_total: The token total to report in usage.
        """
        self._reply = reply
        self._token_total = token_total

    def generate(
        self,
        messages: list[ChatMessage],
        context: str | None = None,
        tool_registry: ToolRegistry | None = None,
    ) -> ChatResponse:
        """Return a fixed assistant reply regardless of input.

        Args:
            messages: Ignored.
            context: Ignored.
            tool_registry: Ignored.

        Returns:
            A ChatResponse with the configured reply and zero token usage.
        """
        return ChatResponse(
            message=ChatMessage(role=Role.ASSISTANT, content=self._reply),
            usage=TokenUsage(total=self._token_total),
        )
