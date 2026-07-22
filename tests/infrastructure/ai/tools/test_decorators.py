from typing import Any

from app.application.ports.tool_registry import ToolDefinition, ToolParameter
from app.infrastructure.ai.tools.decorators import (
    TOOL_DEPENDENCIES_ATTR,
    TOOL_METADATA_ATTR,
    tool,
)


def test_tool_attaches_definition() -> None:
    @tool(name="my_tool", description="A test tool.")
    def my_tool(_arguments: dict[str, Any]) -> str:
        return "ok"

    definition: ToolDefinition = getattr(my_tool, TOOL_METADATA_ATTR)
    assert definition.name == "my_tool"
    assert definition.description == "A test tool."
    assert definition.parameters == []


def test_tool_attaches_parameters() -> None:
    param = ToolParameter(name="query", type="string", description="A query.")

    @tool(name="my_tool", description="A test tool.", parameters=[param])
    def my_tool(_arguments: dict[str, Any]) -> str:
        return "ok"

    definition: ToolDefinition = getattr(my_tool, TOOL_METADATA_ATTR)
    assert definition.parameters == [param]


def test_tool_dependencies_defaults_to_empty() -> None:
    @tool(name="my_tool", description="A test tool.")
    def my_tool(_arguments: dict[str, Any]) -> str:
        return "ok"

    assert getattr(my_tool, TOOL_DEPENDENCIES_ATTR) == {}


def test_tool_dependencies_are_attached() -> None:
    @tool(name="my_tool", description="A test tool.", dependencies={"db": None})
    def my_tool(_arguments: dict[str, Any]) -> str:
        return "ok"

    assert getattr(my_tool, TOOL_DEPENDENCIES_ATTR) == {"db": None}


def test_tool_returns_original_callable() -> None:
    @tool(name="my_tool", description="A test tool.")
    def my_tool(_arguments: dict[str, Any]) -> str:
        return "result"

    assert my_tool({}) == "result"
