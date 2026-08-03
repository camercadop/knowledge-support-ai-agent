import pytest

from app.infrastructure.ai.mock.tool_registry import MockToolRegistry


def test_list_definitions_returns_one_per_handler() -> None:
    registry = MockToolRegistry(handlers={"tool_a": lambda _: "a", "tool_b": lambda _: "b"})
    names = {d.name for d in registry.list_definitions()}
    assert names == {"tool_a", "tool_b"}


def test_list_definitions_returns_empty_when_no_handlers() -> None:
    registry = MockToolRegistry()
    assert registry.list_definitions() == []


def test_execute_calls_registered_handler() -> None:
    registry = MockToolRegistry(handlers={"tool_a": lambda _: "result"})
    assert registry.execute("tool_a", {}) == "result"


def test_execute_forwards_arguments_to_handler() -> None:
    registry = MockToolRegistry(handlers={"echo": lambda args: args["value"]})
    assert registry.execute("echo", {"value": "hello"}) == "hello"


def test_execute_raises_key_error_for_unregistered_tool() -> None:
    registry = MockToolRegistry()
    with pytest.raises(KeyError):
        registry.execute("unknown", {})
