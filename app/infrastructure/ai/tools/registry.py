import importlib
import logging
import pkgutil
from collections.abc import Callable
from typing import Any

from sqlalchemy.orm import Session

from app.application.ports.tool_registry import ToolDefinition, ToolRegistry
from app.infrastructure.ai.tools.decorators import (
    TOOL_METADATA_ATTR,
    TOOL_REQUIRES_DB_ATTR,
)

logger = logging.getLogger(__name__)

_TOOLS_PACKAGE = "app.infrastructure.ai.tools"


class ConcreteToolRegistry(ToolRegistry):
    """Tool registry that stores callables and their definitions in memory.

    Register tools via register(). The registry dispatches execute() calls
    by name to the matching callable. Use this as the production implementation
    injected into the chat model.
    """

    def __init__(self) -> None:
        """Initialize with empty tool and definition stores."""
        self._tools: dict[str, Callable[[dict[str, Any]], str]] = {}
        self._definitions: dict[str, ToolDefinition] = {}

    def register(
        self,
        definition: ToolDefinition,
        handler: Callable[[dict[str, Any]], str],
    ) -> None:
        """Register a tool with its definition and callable handler.

        Args:
            definition: Metadata describing the tool to the LLM.
            handler: Callable that receives the LLM-supplied arguments
                and returns a string result.
        """
        self._tools[definition.name] = handler
        self._definitions[definition.name] = definition
        logger.info("Registered tool: %s", definition.name)

    def list_definitions(self) -> list[ToolDefinition]:
        """Return the definitions of all registered tools.

        Returns:
            List of ToolDefinition objects describing each available tool.
        """
        return list(self._definitions.values())

    def execute(self, name: str, arguments: dict[str, Any]) -> str:
        """Execute a registered tool by name with the given arguments.

        Args:
            name: The name of the tool to execute.
            arguments: A dict of argument names to values as provided by the LLM.

        Returns:
            The tool result as a plain string.

        Raises:
            KeyError: If no tool with the given name is registered.
        """
        logger.info("Executing tool: %s", name)
        return self._tools[name](arguments)


def build_tool_registry(db: Session) -> ConcreteToolRegistry:
    """Discover and register all @tool-decorated callables in the tools package.

    Scans every module in app.infrastructure.ai.tools for callables decorated
    with @tool. Callables with requires_db=True are treated as factories and
    called with db to produce the handler.

    Args:
        db: The active database session, forwarded to db-scoped tool factories.

    Returns:
        A ConcreteToolRegistry with all discovered tools registered.
    """
    registry = ConcreteToolRegistry()
    package = importlib.import_module(_TOOLS_PACKAGE)

    for module_info in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{_TOOLS_PACKAGE}.{module_info.name}")
        for attr_name in dir(module):
            obj = getattr(module, attr_name)
            if not callable(obj) or not hasattr(obj, TOOL_METADATA_ATTR):
                continue
            definition: ToolDefinition = getattr(obj, TOOL_METADATA_ATTR)
            requires_db: bool = getattr(obj, TOOL_REQUIRES_DB_ATTR, False)
            handler = obj(db) if requires_db else obj
            registry.register(definition, handler)

    return registry
