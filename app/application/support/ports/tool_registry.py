from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolParameter:
    """A single parameter definition for a tool."""

    name: str
    type: str
    description: str
    required: bool = True


@dataclass(frozen=True)
class ToolDefinition:
    """Metadata describing a tool exposed to the LLM."""

    name: str
    description: str
    parameters: list[ToolParameter]


class ToolRegistry(ABC):
    """Port that defines the contract for the tool registry.

    Implementations live in infrastructure/ai/tools/. Use this interface
    in application-layer use cases to remain decoupled from any specific
    tool implementation. The registry is responsible for listing available
    tools and dispatching execution by name.
    """

    @abstractmethod
    def list_definitions(self) -> list[ToolDefinition]:
        """Return the definitions of all registered tools.

        Returns:
            List of ToolDefinition objects describing each available tool.
        """

    @abstractmethod
    def execute(self, name: str, arguments: dict[str, Any]) -> str:
        """Execute a registered tool by name with the given arguments.

        Args:
            name: The name of the tool to execute.
            arguments: A dict of argument names to values as provided by the LLM.

        Returns:
            The tool result as a plain string to be fed back to the LLM.

        Raises:
            KeyError: If no tool with the given name is registered.
        """
