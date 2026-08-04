# Writing Agent Tools

This document describes how to implement an agent tool in this project.

## Purpose

Tools live in `app/infrastructure/ai/tools/` and are callable units exposed to the LLM via the tool registry. Each tool is discovered automatically at registry build time — no manual registration is required.

## Two Patterns

### Stateless tool

Use this when the tool has no infrastructure dependencies.

```python
from typing import Any

from app.infrastructure.ai.tools.decorators import tool


@tool(
    name="get_current_date",
    description="Returns today's date in ISO 8601 format (YYYY-MM-DD).",
)
def get_current_date(_arguments: dict[str, Any]) -> str:
    """Return today's date in ISO 8601 format.

    Args:
        _arguments: Unused. Accepted for uniform tool call signature.

    Returns:
        Today's date as a string in YYYY-MM-DD format.
    """
    return date.today().isoformat()
```

### Factory-based tool

Use this when the tool requires injected dependencies (e.g. a database session or an infrastructure client). The decorated callable is a factory that receives the resolved dependencies and returns the tool instance.

```python
from typing import Any

from sqlalchemy.orm import Session

from app.application.ports.embedding_model import EmbeddingModel
from app.application.ports.tool_registry import ToolParameter
from app.infrastructure.ai.embeddings.openai import OpenAIEmbeddingModel
from app.infrastructure.ai.tools.decorators import tool


@tool(
    name="my_tool",
    description="Does something useful.",
    parameters=[
        ToolParameter(name="query", type="string", description="The input query."),
    ],
    dependencies={
        "db": None,
        "embedding_model": OpenAIEmbeddingModel,
    },
)
def my_tool_factory(db: Session, embedding_model: EmbeddingModel) -> "MyTool":
    """Construct a MyTool for the given session and embedding model.

    Args:
        db: Active database session.
        embedding_model: Embedding model used by the tool.

    Returns:
        A fully wired MyTool instance.
    """
    return MyTool(db=db, embedding_model=embedding_model)


class MyTool:
    """Does something useful with the knowledge base."""

    def __init__(self, db: Session, embedding_model: EmbeddingModel) -> None:
        """Initialize with the required dependencies."""
        self._db = db
        self._embedding_model = embedding_model

    def __call__(self, arguments: dict[str, Any]) -> str:
        """Execute the tool with LLM-supplied arguments.

        Args:
            arguments: Must contain a "query" key.

        Returns:
            The tool result as a plain string.
        """
        ...
```

## Dependency Injection

The `dependencies` dict maps constructor parameter names to zero-argument factories:

| Key | Value | Resolved as |
|-----|-------|-------------|
| `"db"` | `None` | The active `Session` — reserved, always injected by the registry |
| Any other key | A zero-argument callable (e.g. a class) | Called with no arguments to produce the dependency |

Declaring `"db"` with a non-`None` factory raises a `ValueError` at registry build time.

## Discovery

The registry scans every module in `app.infrastructure.ai.tools` at build time. Any callable with `_tool_metadata` attached (set by `@tool`) is registered automatically. No import or registration call is needed outside the tool module itself.

## Rules

- One module per tool, named after the tool in snake_case: `app/infrastructure/ai/tools/<tool_name>.py`.
- The `name` passed to `@tool` must be unique across all tools — duplicate names raise a `ValueError` at registry build time.
- Stateless tools must accept `arguments: dict[str, Any]` and return `str`.
- Factory-based tools must place the factory function and the tool class in the same module.
- The tool class must implement `__call__(self, arguments: dict[str, Any]) -> str`.
- Never put business logic in a tool — tools are infrastructure adapters. Query and retrieval logic belongs in `app/application/`.
- All public methods must have docstrings.

## Input Validation

The `ConcreteToolRegistry.execute()` method validates all tool arguments against the declared `ToolParameter` schema before dispatching to the handler. Validation checks:

- **Required parameters** — missing required params raise `ValueError`.
- **Unexpected parameters** — params not declared in the tool definition raise `ValueError`.
- **Type mismatches** — values that don't match the declared `ToolParameter.type` raise `ValueError`.

The supported type mappings are:

| `ToolParameter.type` | Python type |
|----------------------|-------------|
| `"string"` | `str` |
| `"integer"` | `int` |
| `"boolean"` | `bool` |
| `"number"` | `float` |

Validation failures are surfaced as tool execution errors to the LLM.

## Query Sanitization

Tools that accept user-supplied query strings should sanitize them before use. The `search_documents` tool demonstrates this pattern — it strips whitespace, removes injection characters (newlines, null bytes, control characters), and enforces a maximum query length.

## Execution Timeout

The `ConcreteToolRegistry` enforces a configurable execution timeout on all tool calls. If a tool exceeds the timeout, the registry returns a fixed `"Tool execution timed out."` message to the LLM instead of raising. The default timeout is 30 seconds, configurable via the `timeout` parameter to `ConcreteToolRegistry.__init__()`.
