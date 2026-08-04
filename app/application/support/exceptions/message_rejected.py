class MessageRejected(Exception):
    """Raised by a MessageSanitizer when a user message is deemed invalid.

    Signals that the message must not enter the prompt pipeline. The reason
    is logged by the use case and never exposed to the client.

    Args:
        reason: Human-readable description of why the message was rejected.
    """

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason
