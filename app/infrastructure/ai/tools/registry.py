import importlib
import logging
import pkgutil
from collections.abc import Callable
from typing import Any

from sqlalchemy.orm import Session

from app.application.ports.tool_registry import ToolDefinition, ToolRegistry
from app.infrastructure.ai.tools.decorators import (
    DB_DEPENDENCY_KEY,
    TOOL_DEPENDENCIES_ATTR,
    TOOL_METADATA_ATTR,
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


def _validate_dependencies(tool_name: str, deps: dict[str, Any]) -> None:
    """Validate that the reserved 'db' key is not given a non-None factory.

    Args:
        tool_name: Name of the tool being validated, used in the error message.
        deps: The dependencies dict attached to the tool.

    Raises:
        ValueError: If 'db' is declared with a non-None factory.
    """
    if DB_DEPENDENCY_KEY in deps and deps[DB_DEPENDENCY_KEY] is not None:
        raise ValueError(
            f"Tool '{tool_name}' declares '{DB_DEPENDENCY_KEY}' with a "
            f"non-None factory. The '{DB_DEPENDENCY_KEY}' key is reserved and "
            "always resolved by the registry from the active Session."
        )


def build_tool_registry(db: Session) -> ConcreteToolRegistry:
    """Discover and register all @tool-decorated callables in the tools package.

    Scans every module in app.infrastructure.ai.tools for callables decorated
    with @tool. If a tool declares dependencies, it is treated as a factory
    called with the resolved dependencies as kwargs. The reserved "db" key is
    always resolved from the active Session — declaring it with a non-None
    factory raises a ValueError at build time.

    Args:
        db: The active database session, injected for tools that declare "db"
            in their dependencies.

    Returns:
        A ConcreteToolRegistry with all discovered tools registered.

    Raises:
        ValueError: If a tool declares "db" with a non-None factory.
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
            deps: dict[str, Callable[[], Any] | None] = getattr(obj, TOOL_DEPENDENCIES_ATTR, {})

            _validate_dependencies(definition.name, deps)

            if not deps:
                registry.register(definition, obj)
                continue

            resolved = {
                key: db if key == DB_DEPENDENCY_KEY else factory()  # type: ignore[misc]
                for key, factory in deps.items()
                if factory is not None or key == DB_DEPENDENCY_KEY
            }
            registry.register(definition, obj(**resolved))

    return registry
