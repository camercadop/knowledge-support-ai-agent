from abc import ABC, abstractmethod


class MessageSanitizer(ABC):
    """Port for sanitizing user messages before they enter the prompt pipeline.

    Implementations live in infrastructure/ai/. Use this interface in
    application-layer use cases to remain decoupled from any specific
    sanitization strategy or third-party guardrails library.
    """

    @abstractmethod
    def sanitize(self, message: str) -> str:
        """Return a sanitized copy of the user message.

        Strips or neutralizes content that could manipulate LLM behavior,
        such as prompt injection directives or instruction override attempts.
        The original message is never mutated.

        Args:
            message: Raw user message text.

        Returns:
            Sanitized message safe to inject into the prompt pipeline.
        """
