import concurrent.futures
import importlib
import logging
import pkgutil
from collections.abc import Callable
from typing import Any

from sqlalchemy.orm import Session

from app.application.support.ports.tool_registry import ToolDefinition, ToolRegistry
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

    TYPE_MAP: dict[str, type] = {
        "string": str,
        "integer": int,
        "boolean": bool,
        "number": float,
    }

    def __init__(self, timeout: float = 30.0) -> None:
        """Initialize with empty tool and definition stores.

        Args:
            timeout: Maximum seconds to wait for a tool execution
                before returning a timeout message.
        """
        self._tools: dict[str, Callable[[dict[str, Any]], str]] = {}
        self._definitions: dict[str, ToolDefinition] = {}
        self._timeout = timeout

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

        Raises:
            ValueError: If a tool with the same name is already registered.
        """
        if definition.name in self._definitions:
            raise ValueError(f"Tool '{definition.name}' is already registered.")
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
            If the tool execution exceeds the configured timeout, returns
            a fixed timeout message.

        Raises:
            KeyError: If no tool with the given name is registered.
            ValueError: If argument validation fails (missing required params,
                unexpected params, or type mismatches).
        """
        logger.info("Executing tool: %s", name)
        definition = self._definitions[name]
        self._validate_arguments(name, definition, arguments)
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self._tools[name], arguments)
            try:
                return future.result(timeout=self._timeout)
            except concurrent.futures.TimeoutError:
                logger.warning(
                    "Tool '%s' execution timed out after %.1fs", name, self._timeout
                )
                return "Tool execution timed out."

    def _validate_arguments(
        self,
        tool_name: str,
        definition: ToolDefinition,
        arguments: dict[str, Any],
    ) -> None:
        """Validate that arguments match the tool's declared parameter schema.

        Checks that all required parameters are present, no unexpected
        parameters are included, and each argument's value matches the
        declared type.

        Args:
            tool_name: Name of the tool being validated, used in error messages.
            definition: The tool's parameter definitions.
            arguments: The arguments dict supplied by the LLM.

        Raises:
            ValueError: On missing required params, unexpected params,
            or type mismatches.
        """
        param_names = {p.name for p in definition.parameters}

        for param in definition.parameters:
            if param.required and param.name not in arguments:
                raise ValueError(
                    f"Tool '{tool_name}' is missing required parameter '{param.name}'."
                )

        for key in arguments:
            if key not in param_names:
                raise ValueError(
                    f"Tool '{tool_name}' received unexpected parameter '{key}'."
                )

        for param in definition.parameters:
            if param.name in arguments:
                expected_type = self.TYPE_MAP.get(param.type)
                if expected_type is not None and not isinstance(
                    arguments[param.name], expected_type
                ):
                    param_type = type(arguments[param.name]).__name__
                    raise ValueError(
                        f"Tool '{tool_name}' parameter '{param.name}' expected type "
                        f"'{param.type}' but got '{param_type}'."
                    )


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
        ValueError: If two tools share the same name.
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
            deps: dict[str, Callable[[], Any] | None] = getattr(
                obj, TOOL_DEPENDENCIES_ATTR, {}
            )

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
