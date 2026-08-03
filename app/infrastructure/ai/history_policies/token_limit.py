from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.application.support.ports.chat_model import ChatMessage

from app.application.support.ports.message_retention_policy import (
    MessageRetentionPolicy,
)


class TokenLimitPolicy(MessageRetentionPolicy):
    """Token limit retention policy.

    Drops oldest messages (excluding the current user message) until the total
    token count fits within the configured budget. The current user message is
    always protected from removal.
    """

    def __init__(
        self, max_tokens: int, token_calculator: Callable[[str], int] | None = None
    ):
        """Initialize the token limit policy.

        Args:
            max_tokens: Maximum allowed tokens in the message history.
            token_calculator: Optional function to calculate tokens for a message.
                Defaults to using the tiktoken encoding specified in settings.
        """
        self.max_tokens = max_tokens
        self.token_calculator = token_calculator

    def apply(self, messages: list[ChatMessage]) -> list[ChatMessage]:
        """Apply token limit policy to the message list.

        Args:
            messages: Ordered list of chat messages (user, assistant turns).

        Returns:
            Ordered list of messages with token count within budget,
            or the original list if budget is already met.
        """
        if not self.max_tokens:
            return messages

        total_tokens = self._calculate_total_tokens(messages)
        if total_tokens <= self.max_tokens:
            return messages

        return self._trim_by_tokens(messages, total_tokens)

    def _calculate_total_tokens(self, messages: list[ChatMessage]) -> int:
        """Calculate total tokens for a list of messages."""
        if not messages:
            return 0

        if self.token_calculator:
            return sum(self.token_calculator(m.content) for m in messages)

        import tiktoken

        from app.config.settings import settings

        encoding = tiktoken.get_encoding(settings.retrieval_encoding)
        return sum(len(encoding.encode(m.content)) for m in messages)

    def _trim_by_tokens(
        self, messages: list[ChatMessage], total_tokens: int
    ) -> list[ChatMessage]:
        """Trim messages from oldest to fit token budget.

        Current user message (last message if it's user,
        or second-to-last if followed by assistant) is always protected.
        """
        import tiktoken

        from app.config.settings import settings

        encoding = tiktoken.get_encoding(settings.retrieval_encoding)
        protected_message_count = self._get_protected_message_count(messages)
        protected_start_index = len(messages) - protected_message_count

        protected_tokens = self._calculate_total_tokens(
            messages[protected_start_index:]
        )
        budget = self.max_tokens - protected_tokens
        kept_tokens = 0

        kept: list[ChatMessage] = []
        for message in reversed(messages[:protected_start_index]):
            message_tokens = len(encoding.encode(message.content))
            if kept_tokens + message_tokens > budget:
                break
            kept.insert(0, message)
            kept_tokens += message_tokens

        return kept + messages[protected_start_index:]

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
