import logging

from app.application.support.ports.chat_model import ChatMessage
from app.application.support.ports.message_retention_policy import (
    MessageRetentionPolicy,
)

logger = logging.getLogger(__name__)


class ConversationHistoryOptimizer:
    """Service that applies retention policies to conversation history.

    This service applies a sequence of retention policies to conversation history
    before it is passed to the LLM for generation. Policies include token limit
    enforcement, message count management, role filtering, and message summarization.

    The optimizer ensures that the current user message is always preserved and
    applies policies in the order they are configured.
    """

    def __init__(self, policies: list[MessageRetentionPolicy]):
        """Initialize the history optimizer.

        Args:
            policies: Ordered list of retention policies to apply.
                Policies are applied in the order they appear in this list.
                Each policy must implement the MessageRetentionPolicy interface.
        """
        self.policies = policies

    def optimize_history(self, messages: list[ChatMessage]) -> list[ChatMessage]:
        """Apply all retention policies to the message history.

        Args:
            messages: Ordered list of conversation messages, where the last
                message(s) represent the most recent turn.

        Returns:
            Ordered list of optimized messages with retention policies applied.
        """
        if not messages:
            return messages

        logger.info(
            "Applying %s retention policies to %s messages",
            len(self.policies),
            len(messages),
        )

        optimized_messages = messages
        for policy in self.policies:
            logger.debug("Applying policy: %s", policy.__class__.__name__)
            optimized_messages = policy.apply(optimized_messages)

        logger.info("Optimized message count: %s", len(optimized_messages))
        return optimized_messages
