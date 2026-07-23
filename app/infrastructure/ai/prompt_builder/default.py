from typing import TypedDict

from app.application.ports.chat_model import ChatMessage, Role
from app.application.ports.prompt_builder import PromptBuilder


class PromptConfig(TypedDict):
    """Typed configuration bag for DefaultPromptBuilder.

    All keys are required. Source the values from env vars, a database,
    or any other mechanism — the builder does not care about the origin.
    """

    system_instructions: str
    grounded_instructions: str
    no_context_instructions: str


class DefaultPromptBuilder(PromptBuilder):
    """Assembles the provider-agnostic message list for a RAG-grounded chat turn.

    Prepends a system message that combines the base instructions with either
    the retrieved knowledge excerpts or a no-context fallback instruction.
    The prompt strings are injected via a PromptConfig dict, allowing callers to
    source them from env vars, a database, or any other configuration mechanism.
    """

    def __init__(self, config: PromptConfig) -> None:
        """Initialise the builder with the prompt configuration.

        Args:
            config: Typed dict containing system_instructions, grounded_instructions,
                and no_context_instructions.
        """
        self._config = config

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
                f"{self._config['system_instructions']}\n\n{self._config['grounded_instructions']}"
                f"\n\nKnowledge base excerpts:\n{context}"
            )
        else:
            system_content = (
                f"{self._config['system_instructions']}\n\n"
                f"{self._config['no_context_instructions']}"
            )

        return [ChatMessage(role=Role.SYSTEM, content=system_content), *messages]
