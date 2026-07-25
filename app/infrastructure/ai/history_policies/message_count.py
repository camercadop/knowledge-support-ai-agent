from app.application.support.ports.chat_model import ChatMessage
from app.application.support.ports.message_retention_policy import (
    MessageRetentionPolicy,
)


class MessageCountPolicy(MessageRetentionPolicy):
    """Message count retention policy.

    Keeps only the most recent N messages (excluding the current user message)
    to ensure the conversation stays within a reasonable message limit.
    The current user message is always protected from removal.
    """

    def __init__(self, max_messages: int):
        """Initialize the message count policy.

        Args:
            max_messages: Maximum allowed number of messages in the message history.
        """
        self.max_messages = max_messages

    def apply(self, messages: list[ChatMessage]) -> list[ChatMessage]:
        """Apply message count policy to the message list.

        Args:
            messages: Ordered list of chat messages (user, assistant turns).

        Returns:
            Ordered list of messages with count within budget,
            or the original list if budget is already met.
        """
        if not self.max_messages:
            return messages

        if len(messages) <= self.max_messages:
            return messages

        protected_message_count = self._get_protected_message_count(messages)
        max_history_count = self.max_messages - protected_message_count

        return messages[:max_history_count] + messages[-protected_message_count:]

    def _get_protected_message_count(self, messages: list[ChatMessage]) -> int:
        """
        Calculate number of messages that must be protected (current user message).
        """
        if not messages:
            return 0

        last_message = messages[-1]

        if last_message.role.value == "user":
            return 1

        if len(messages) >= 2 and messages[-2].role.value == "user":
            return 2

        return 0
