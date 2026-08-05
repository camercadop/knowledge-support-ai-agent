from app.application.support.ports.query_rewriter import QueryRewriter


class PassthroughQueryRewriter(QueryRewriter):
    """Returns the query unchanged.

    Use this adapter when query rewriting is disabled or not needed.
    """

    def rewrite(self, query: str, history: list[str]) -> str:
        """Return the query unchanged.

        Args:
            query: The current user message text.
            history: Ordered list of previous messages in the conversation.

        Returns:
            The original query string, unmodified.
        """
        return query
