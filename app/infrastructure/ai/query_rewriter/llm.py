import logging

from app.application.support.ports.chat_model import ChatMessage, ChatModel, Role
from app.application.support.ports.query_rewriter import QueryRewriter

logger = logging.getLogger(__name__)


class LLMQueryRewriter(QueryRewriter):
    """Rewrites queries using an LLM chat model.

    Sends the user query and conversation history to the chat model
    with a rewrite prompt and returns the model's response as the
    rewritten query.

    Args:
        chat_model: The chat model provider used to generate the rewrite.
        prompt: The system prompt instructing the model how to rewrite queries.
    """

    def __init__(self, chat_model: ChatModel, prompt: str) -> None:
        self._chat_model = chat_model
        self._prompt = prompt

    def rewrite(self, query: str, history: list[str]) -> str:
        """Rewrite a user query using the LLM.

        Builds a conversation with the rewrite prompt as the system message,
        the conversation history as prior user/assistant turns, and the
        current query as the final user message.

        Args:
            query: The current user message text.
            history: Ordered list of previous messages in the conversation.

        Returns:
            The rewritten query string from the LLM.
        """
        messages: list[ChatMessage] = [
            ChatMessage(role=Role.SYSTEM, content=self._prompt),
        ]
        for turn in history:
            messages.append(ChatMessage(role=Role.USER, content=turn))
            messages.append(
                ChatMessage(role=Role.ASSISTANT, content=turn),
            )
        messages.append(ChatMessage(role=Role.USER, content=query))

        logger.info("Rewriting query with LLM")
        response = self._chat_model.generate(messages)
        rewritten = response.message.content
        logger.info("Query rewritten successfully")
        return rewritten
