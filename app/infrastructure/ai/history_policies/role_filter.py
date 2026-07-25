from app.application.support.ports.chat_model import ChatMessage


class RoleFilterPolicy:
    """Role filter retention policy.

    Filters messages based on their roles. Only messages with roles in the
    allowed_roles list are kept; messages with roles in blocked_roles are
    removed. The current user message is always protected from removal.
    """

    def __init__(self, allowed_roles: list[str], blocked_roles: list[str] | None = None):
        """Initialize the role filter policy.

        Args:
            allowed_roles: List of roles to keep (e.g., ["user", "assistant"]).
            blocked_roles: List of roles to explicitly block.
        """
        self.allowed_roles = allowed_roles
        self.blocked_roles = blocked_roles or []

    def apply(self, messages: list[ChatMessage]) -> list[ChatMessage]:
        """Apply role filter policy to the message list.

        Args:
            messages: Ordered list of chat messages (user, assistant turns).

        Returns:
            Ordered list of messages with filtered roles, or the original list
            if no messages need to be filtered.
        """
        blocked_roles_set = set(self.blocked_roles)

        def is_valid_message(message: ChatMessage) -> bool:
            role_value = message.role.value
            return (
                role_value in self.allowed_roles and role_value not in blocked_roles_set
            )

        filtered_messages = []
        protected_messages = []

        for message in messages:
            if self._is_protected_message(message, messages):
                protected_messages.append(message)
            elif is_valid_message(message):
                filtered_messages.append(message)

        return filtered_messages + protected_messages

    def _is_protected_message(
        self, message: ChatMessage, all_messages: list[ChatMessage]
    ) -> bool:
        """Check if a message is protected (current user message)."""
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
