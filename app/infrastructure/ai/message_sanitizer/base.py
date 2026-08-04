from app.application.support.ports.message_sanitizer import MessageSanitizer


class CompositeSanitizer(MessageSanitizer):
    """Applies a list of MessageSanitizer instances in order.

    Use this to chain multiple sanitization strategies without coupling them.
    Each sanitizer receives the output of the previous one.

    Args:
        sanitizers: Ordered list of MessageSanitizer instances to apply.
    """

    def __init__(self, sanitizers: list[MessageSanitizer]) -> None:
        self._sanitizers = sanitizers

    def sanitize(self, message: str) -> str:
        """Pass the message through each sanitizer in sequence.

        Args:
            message: Raw user message text.

        Returns:
            Message after all sanitizers have been applied.
        """
        for sanitizer in self._sanitizers:
            message = sanitizer.sanitize(message)
        return message
