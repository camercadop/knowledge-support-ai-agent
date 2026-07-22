from abc import ABC, abstractmethod

from app.application.ports.chat_model import ChatMessage


class PromptBuilder(ABC):
    """Port that defines the contract for assembling a provider-agnostic message list.

    Implementations live in infrastructure/ai/chat/. Use this interface in
    application-layer use cases to remain decoupled from any specific prompt strategy.
    """

    @abstractmethod
    def build(
        self,
        messages: list[ChatMessage],
        context: str | None = None,
    ) -> list[ChatMessage]:
        """Assemble the full message list to send to the chat model.

        Prepends a system message that incorporates the base instructions and,
        when available, the retrieved knowledge context. Returns the complete
        ordered list ready to pass to ChatModel.generate().

        Args:
            messages: Ordered conversation history (user and assistant turns).
            context: Optional retrieved knowledge chunks to ground the response.
                When None, the system prompt instructs the model to acknowledge
                it has no context rather than fabricate an answer.

        Returns:
            Full ordered list of ChatMessage objects starting with the system message.
        """
