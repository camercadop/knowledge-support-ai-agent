from collections.abc import Callable
from typing import Any, TypeVar

from app.application.ports.tool_registry import ToolDefinition, ToolParameter

F = TypeVar("F", bound=Callable[..., Any])

TOOL_METADATA_ATTR = "_tool_metadata"
TOOL_REQUIRES_DB_ATTR = "_tool_requires_db"


def tool(
    name: str,
    description: str,
    parameters: list[ToolParameter] | None = None,
    requires_db: bool = False,
) -> Callable[[F], F]:
    """Mark a callable as a discoverable tool.

    Attaches a ToolDefinition and a requires_db flag to the callable so the
    registry can discover and register it automatically. When requires_db is
    True, the callable is treated as a factory that receives a Session and
    returns the actual tool handler.

    Args:
        name: Tool name exposed to the LLM.
        description: Human-readable description of what the tool does.
        parameters: List of ToolParameter definitions. Defaults to empty.
        requires_db: Set to True when the callable is a factory that accepts
            a Session argument to construct the handler.

    Returns:
        The original callable with metadata attributes attached.

    Example:
        Simple tool with no dependencies::

            @tool(name="get_current_date", description="Returns today's date.")
            def get_current_date(_arguments: dict[str, Any]) -> str:
                return date.today().isoformat()

        Tool that requires a database session::

            @tool(
                name="search_documents",
                description="Search the knowledge base.",
                parameters=[ToolParameter(name="query", type="string", description="...")],
                requires_db=True,
            )
            def search_documents_factory(db: Session) -> SearchDocumentsTool:
                return SearchDocumentsTool(embedding_model=..., vector_store=PgVectorStore(db))
    """

    def decorator(fn: F) -> F:
        setattr(fn, TOOL_METADATA_ATTR, ToolDefinition(
            name=name,
            description=description,
            parameters=parameters or [],
        ))
        setattr(fn, TOOL_REQUIRES_DB_ATTR, requires_db)
        return fn

    return decorator
