import pytest
from sqlalchemy.orm import Session

from app.application.ports.tool_registry import ToolDefinition
from app.infrastructure.ai.tools.registry import (
    ConcreteToolRegistry,
    _validate_dependencies,
    build_tool_registry,
)

# --- ConcreteToolRegistry ---


def _make_registry(*names: str) -> ConcreteToolRegistry:
    registry = ConcreteToolRegistry()
    for name in names:
        registry.register(
            ToolDefinition(name=name, description="", parameters=[]),
            lambda _arguments, n=name: n,
        )
    return registry


def test_list_definitions_returns_registered_tools() -> None:
    registry = _make_registry("tool_a", "tool_b")
    names = {d.name for d in registry.list_definitions()}
    assert names == {"tool_a", "tool_b"}


def test_execute_calls_registered_handler() -> None:
    registry = _make_registry("tool_a")
    assert registry.execute("tool_a", {}) == "tool_a"


def test_execute_raises_key_error_for_unknown_tool() -> None:
    registry = _make_registry()
    with pytest.raises(KeyError):
        registry.execute("unknown", {})


def test_register_overwrites_existing_tool() -> None:
    registry = ConcreteToolRegistry()
    definition = ToolDefinition(name="my_tool", description="", parameters=[])
    registry.register(definition, lambda _: "first")
    registry.register(definition, lambda _: "second")
    assert registry.execute("my_tool", {}) == "second"


# --- build_tool_registry ---


def test_build_tool_registry_discovers_get_current_date(db: Session) -> None:
    registry = build_tool_registry(db)
    names = {d.name for d in registry.list_definitions()}
    assert "get_current_date" in names


def test_build_tool_registry_discovers_search_documents(db: Session) -> None:
    registry = build_tool_registry(db)
    names = {d.name for d in registry.list_definitions()}
    assert "search_documents" in names


def test_validate_dependencies_raises_when_db_has_non_none_factory() -> None:
    with pytest.raises(ValueError, match="reserved"):
        _validate_dependencies("bad_tool", {"db": lambda: None})


def test_validate_dependencies_passes_when_db_is_none() -> None:
    _validate_dependencies("ok_tool", {"db": None})  # should not raise


def test_validate_dependencies_passes_when_no_db_key() -> None:
    _validate_dependencies(
        "ok_tool", {"embedding_model": lambda: None}
    )  # should not raise


def test_build_tool_registry_get_current_date_returns_date_string(db: Session) -> None:
    import re

    registry = build_tool_registry(db)
    result = registry.execute("get_current_date", {})
    assert re.match(r"\d{4}-\d{2}-\d{2}", result)
