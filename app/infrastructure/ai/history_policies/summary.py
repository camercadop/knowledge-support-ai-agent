from app.application.support.ports.chat_model import ChatMessage, ChatModel, Role
from app.application.support.ports.message_retention_policy import (
    MessageRetentionPolicy,
)
from app.application.support.ports.tool_registry import ToolRegistry


class SummaryPolicy(MessageRetentionPolicy):
    """Summary retention policy.

    Summarizes older messages via the ChatModel when the conversation exceeds
    a token or message limit. The summary is generated for the oldest messages
    that need to be removed, preserving the most recent ones.
    """

    def __init__(
        self,
        chat_model: ChatModel,
        max_summary_tokens: int = 1000,
        max_summary_messages: int = 5,
        prefix: str = "Previous conversation summary:\n\n",
        tool_registry: ToolRegistry | None = None,
    ):
        """Initialize the summary policy.

        Args:
            chat_model: ChatModel used to generate summaries.
            max_summary_tokens: Maximum tokens allowed in a summary.
            max_summary_messages: Maximum number of messages to summarize at once.
            prefix: Text prefix added to each summary message.
            tool_registry: Optional tool registry for tool calling during summarization.
        """
        self.chat_model = chat_model
        self.max_summary_tokens = max_summary_tokens
        self.max_summary_messages = max_summary_messages
        self.prefix = prefix
        self.tool_registry = tool_registry

    def apply(self, messages: list[ChatMessage]) -> list[ChatMessage]:
        """Apply summary policy to the message list.

        Args:
            messages: Ordered list of chat messages (user, assistant turns).

        Returns:
            Ordered list of messages with summarized history,
            or the original list if no summary was needed.
        """
        if len(messages) <= self.max_summary_messages:
            return messages

        summary_messages = self._create_summary_messages(messages)
        return summary_messages

    def _create_summary_messages(
        self, messages: list[ChatMessage]
    ) -> list[ChatMessage]:
        """Create summary messages for older messages."""
        summary_messages: list[ChatMessage] = []
        messages_to_summarize: list[ChatMessage] = []

        for message in messages:
            summary_message = self._get_or_create_summary_for_batch(
                messages_to_summarize, message
            )

            if summary_message:
                summary_messages.append(summary_message)
                messages_to_summarize = []

            if len(summary_messages) >= 10:
                break

            if not self._is_current_user_message(message, messages):
                messages_to_summarize.append(message)

        return summary_messages

    def _get_or_create_summary_for_batch(
        self, messages: list[ChatMessage], last_message: ChatMessage
    ) -> ChatMessage | None:
        """Get or create a summary for a batch of messages."""
        if not messages:
            return None

        summary_content = self._summarize_messages(messages, last_message)
        if not summary_content:
            return None

        summary_message = ChatMessage(
            role=Role.ASSISTANT,
            content=summary_content,
        )

        return summary_message

    def _summarize_messages(
        self, messages: list[ChatMessage], last_message: ChatMessage
    ) -> str | None:
        """Generate a summary for a batch of messages."""
        try:
            context_messages = []

            context_messages.extend(messages)

            summary_prompt = self.prefix
            context_messages.append(
                ChatMessage(role=Role.SYSTEM, content=summary_prompt)
            )

            response = self.chat_model.generate(
                context_messages, tool_registry=self.tool_registry
            )

            return response.message.content

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to generate summary: {e}")

            return None

    def _is_current_user_message(
        self, message: ChatMessage, all_messages: list[ChatMessage]
    ) -> bool:
        """Check if a message is the current user message that should be preserved."""
        if not all_messages:
            return False

        last_message = all_messages[-1]

        if message is last_message and last_message.role.value == "user":
            return True

        if (
            len(all_messages) >= 2
            and message is all_messages[-2]
            and all_messages[-1].role.value == "assistant"
            and all_messages[-2].role.value == "user"
        ):
            return True

        return False
