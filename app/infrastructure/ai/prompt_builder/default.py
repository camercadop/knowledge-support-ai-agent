from app.application.ports.chat_model import ChatMessage, Role
from app.application.ports.prompt_builder import PromptBuilder

_SYSTEM_PROMPT = (
    "You are a helpful support assistant. Answer questions clearly and concisely."
)

_GROUNDED_INSTRUCTIONS = (
    "Answer using only the knowledge base excerpts provided below. "
    "If the excerpts do not contain enough information to answer, say you don't know."
)

_NO_CONTEXT_INSTRUCTIONS = (
    "You have no knowledge base context available for this query. "
    "Do not fabricate information. "
    "Tell the user you don't have enough information to answer."
)


class DefaultPromptBuilder(PromptBuilder):
    """Assembles the provider-agnostic message list for a RAG-grounded chat turn.

    Prepends a system message that combines the base instructions with either
    the retrieved knowledge excerpts or a no-context fallback instruction.
    """

    def build(
        self,
        messages: list[ChatMessage],
        context: str | None = None,
    ) -> list[ChatMessage]:
        """Prepend a system message and return the full ordered message list.

        Args:
            messages: Ordered conversation history (user and assistant turns).
            context: Optional retrieved knowledge chunks. When provided, the system
                message instructs the model to answer only from those excerpts.
                When None, the model is instructed to acknowledge the lack of context.

        Returns:
            Full ordered list starting with the system ChatMessage.
        """
        if context:
            system_content = (
                f"{_SYSTEM_PROMPT}\n\n{_GROUNDED_INSTRUCTIONS}"
                f"\n\nKnowledge base excerpts:\n{context}"
            )
        else:
            system_content = f"{_SYSTEM_PROMPT}\n\n{_NO_CONTEXT_INSTRUCTIONS}"

        return [ChatMessage(role=Role.SYSTEM, content=system_content), *messages]
