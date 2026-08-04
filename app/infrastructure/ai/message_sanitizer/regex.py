import re

from app.application.support.ports.message_sanitizer import MessageSanitizer


class RegexMessageSanitizer(MessageSanitizer):
    """Sanitizes user messages by replacing matches against a list of regex patterns.

    Each pattern is applied in order. Use this adapter when injection directives
    can be described as regular expressions. For more complex detection, implement
    a different MessageSanitizer adapter and compose it via CompositeSanitizer.

    Args:
        patterns: List of regex pattern strings to match against the message.
        replacement: String used to replace each match. Defaults to empty string.
    """

    def __init__(self, patterns: list[str], replacement: str = "") -> None:
        self._patterns = [re.compile(p, re.IGNORECASE) for p in patterns]
        self._replacement = replacement

    def sanitize(self, message: str) -> str:
        """Apply each pattern in order and return the sanitized message.

        Args:
            message: Raw user message text.

        Returns:
            Message with all pattern matches replaced by the configured replacement.
        """
        for pattern in self._patterns:
            message = pattern.sub(self._replacement, message)
        return message
