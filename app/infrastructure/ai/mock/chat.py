from app.application.ports.chat_model import (
    ChatMessage,
    ChatModel,
    ChatResponse,
    Role,
    TokenUsage,
)


class MockChatModel(ChatModel):
    """Stub chat model that returns a fixed reply without making API calls.

    Use in tests to avoid real provider calls and keep the suite deterministic.
    Pass a custom reply to control the returned content.
    """

    def __init__(self, reply: str = "mock reply") -> None:
        """Initialize with the reply text to return on every generate call."""
        self._reply = reply

    def generate(
        self, messages: list[ChatMessage], context: str | None = None
    ) -> ChatResponse:
        """Return a fixed assistant reply regardless of input.

        Args:
            messages: Ignored.
            context: Ignored.

        Returns:
            A ChatResponse with the configured reply and zero token usage.
        """
        return ChatResponse(
            message=ChatMessage(role=Role.ASSISTANT, content=self._reply),
            usage=TokenUsage(total=0),
        )
