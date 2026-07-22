# tools

This sub-package contains the tool registry and all tool implementations available to the LLM.

## Structure

- `decorators.py` — `@tool` decorator that marks a callable as discoverable
- `registry.py` — `ConcreteToolRegistry` and `build_tool_registry` discovery function


## How it works

`build_tool_registry` scans every module in this package at startup and registers any callable decorated with `@tool`. No manual registration is needed.

Tools with dependencies declare them via the `dependencies` argument. The registry resolves each dependency by calling its factory. The reserved `"db"` key is always resolved from the active `Session` — its factory value must be `None`.

## Adding a new tool

### Tool with no dependencies

```python
from app.infrastructure.ai.tools.decorators import tool

@tool(name="my_tool", description="Does something useful.")
def my_tool(arguments: dict[str, Any]) -> str:
    return "result"
```

### Tool with dependencies

```python
from app.infrastructure.ai.tools.decorators import tool
from app.application.ports.tool_registry import ToolParameter

@tool(
    name="my_tool",
    description="Does something useful.",
    parameters=[ToolParameter(name="query", type="string", description="The input.")],
    dependencies={
        "db": None,
        "some_client": SomeClient,
    },
)
def my_tool_factory(db: Session, some_client: SomeClient) -> MyTool:
    return MyTool(db=db, client=some_client)
```

The factory receives all resolved dependencies as keyword arguments and must return a callable that accepts `dict[str, Any]` and returns `str`.
