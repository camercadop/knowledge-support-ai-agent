from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.application.support.ports.chat_model import ChatMessage


class MessageRetentionPolicy(ABC):
    """Port that defines the contract for conversation history optimization policies.

    Implementations live in infrastructure/ai/history_policies/. This interface allows
    the application to apply various strategies to prune or summarize conversation
    history before LLM calls.
    """

    @abstractmethod
    def apply(self, messages: list[ChatMessage]) -> list[ChatMessage]:
        """Apply the retention strategy to the ordered list of messages.

        Args:
            messages: Ordered list of chat messages (user, assistant turns).

        Returns:
            Ordered list of messages after applying the retention policy.
            The current user message must always be protected
            from removal/summarization.
        """
