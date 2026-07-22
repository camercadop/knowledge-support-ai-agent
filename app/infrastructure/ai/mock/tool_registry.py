from collections.abc import Callable
from typing import Any

from app.application.ports.tool_registry import ToolDefinition, ToolRegistry


class MockToolRegistry(ToolRegistry):
    """Stub tool registry for tests that need controlled tool behaviour.

    Pre-register tools via the handlers constructor argument. Use this when
    the test exercises a code path that invokes tools and needs predictable
    results. Use a None tool_registry instead when tool calling is not under
    test at all.
    """

    def __init__(
        self,
        handlers: dict[str, Callable[[dict[str, Any]], str]] | None = None,
    ) -> None:
        """Initialize with an optional map of tool name to callable handler.

        Args:
            handlers: Map of tool name to callable. Defaults to empty.
        """
        self._handlers: dict[str, Callable[[dict[str, Any]], str]] = handlers or {}

    def list_definitions(self) -> list[ToolDefinition]:
        """Return a minimal ToolDefinition for each registered handler.

        Returns:
            One ToolDefinition per registered handler, with no parameters.
        """
        return [
            ToolDefinition(name=name, description="", parameters=[])
            for name in self._handlers
        ]

    def execute(self, name: str, arguments: dict[str, Any]) -> str:
        """Execute the registered handler for the given tool name.

        Args:
            name: The tool name to execute.
            arguments: Arguments forwarded to the handler.

        Returns:
            The string result from the handler.

        Raises:
            KeyError: If no handler is registered for the given name.
        """
        return self._handlers[name](arguments)
