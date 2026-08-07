from typing import TYPE_CHECKING

from app.application.support.ports.chat_model import (
    ChatMessage,
    ChatModel,
    ChatModelOverrides,
    ChatModelSettings,
    ChatResponse,
    Role,
    TokenUsage,
)
from app.application.support.ports.prompt_builder import PromptBuilder
from app.infrastructure.ai.registry import llm_provider

if TYPE_CHECKING:
    from app.application.support.ports.tool_registry import ToolRegistry

@llm_provider("mock", "chat")
class MockChatModel(ChatModel):
    """Stub chat model that returns a fixed reply without making API calls.

    Use in tests to avoid real provider calls and keep the suite deterministic.
    Accepts ``reply`` and ``token_total`` to control the returned response.
    """

    def __init__(
        self,
        prompt_builder: PromptBuilder | None = None,
        settings: ChatModelSettings | None = None,
        reply: str = "mock reply",
        token_total: int = 0,
    ) -> None:
        """Store the reply and token total to return from generate.

        Args:
            prompt_builder: Ignored. Accepted to satisfy the ChatModel contract.
            settings: Ignored. Accepted to satisfy the ChatModel contract.
            reply: The fixed reply string returned by generate.
            token_total: The token count reported in TokenUsage.
        """
        self._reply = reply
        self._token_total = token_total

    def generate(
        self,
        messages: list[ChatMessage],
        tool_registry: ToolRegistry | None = None,
        overrides: ChatModelOverrides | None = None,
    ) -> ChatResponse:
        """Return the configured reply and token total.

        Args:
            messages: Ignored.
            tool_registry: Ignored.
            overrides: Ignored.

        Returns:
            A ChatResponse with the configured reply and token usage.
        """
        return ChatResponse(
            message=ChatMessage(role=Role.ASSISTANT, content=self._reply),
            usage=TokenUsage(total=self._token_total),
            model_used="mock-model",
        )
