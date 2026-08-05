from abc import ABC, abstractmethod


class QueryRewriter(ABC):
    """Port that defines the contract for query rewriting strategies.

    Implementations live in infrastructure/ai/query_rewriter/. Use this
    interface in application-layer use cases to remain decoupled from any
    specific rewriting strategy or LLM provider.
    """

    @abstractmethod
    def rewrite(self, query: str, history: list[str]) -> str:
        """Rewrite a user query, optionally using conversation history.

        Args:
            query: The current user message text.
            history: Ordered list of previous messages in the conversation.

        Returns:
            The rewritten query string, suitable for embedding and retrieval.
        """
