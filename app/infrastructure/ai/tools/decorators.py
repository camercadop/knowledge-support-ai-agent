from collections.abc import Callable
from typing import Any, TypeVar

from app.application.ports.tool_registry import ToolDefinition, ToolParameter

F = TypeVar("F", bound=Callable[..., Any])

TOOL_METADATA_ATTR = "_tool_metadata"
TOOL_DEPENDENCIES_ATTR = "_tool_dependencies"

DB_DEPENDENCY_KEY = "db"


def tool(
    name: str,
    description: str,
    parameters: list[ToolParameter] | None = None,
    dependencies: dict[str, Callable[[], Any] | None] | None = None,
) -> Callable[[F], F]:
    """Mark a callable as a discoverable tool.

    Attaches a ToolDefinition and a dependencies map to the callable so the
    registry can discover, resolve, and register it automatically. If the
    callable has no dependencies, it is used directly as the handler. Otherwise
    it is treated as a factory called with the resolved dependencies as kwargs.

    The reserved key "db" is always resolved by the registry from the active
    Session — its factory value must be None. Passing any other value raises
    a ValueError at registry build time.

    Args:
        name: Tool name exposed to the LLM.
        description: Human-readable description of what the tool does.
        parameters: List of ToolParameter definitions. Defaults to empty.
        dependencies: Map of parameter name to a zero-argument factory, or None
            for the reserved "db" key. Defaults to empty.

    Returns:
        The original callable with metadata attributes attached.

    Example:
        Simple tool with no dependencies:

            @tool(name="get_current_date", description="Returns today's date.")
            def get_current_date(_arguments: dict[str, Any]) -> str:
                return date.today().isoformat()

        Tool with injected dependencies:

            @tool(
                name="search_documents",
                description="Search the knowledge base.",
                parameters=[
                    ToolParameter(
                        name="query", type="string", description="..."
                    )
                ],
                dependencies={
                    "db": None,
                    "embedding_model": OpenAIEmbeddingModel,
                },
            )
            def search_documents_factory(
                db: Session, embedding_model: EmbeddingModel
            ) -> SearchDocumentsTool:
                return SearchDocumentsTool(
                    embedding_model=embedding_model,
                    vector_store=PgVectorStore(db),
                )
    """

    def decorator(fn: F) -> F:
        setattr(fn, TOOL_METADATA_ATTR, ToolDefinition(
            name=name,
            description=description,
            parameters=parameters or [],
        ))
        setattr(fn, TOOL_DEPENDENCIES_ATTR, dependencies or {})
        return fn

    return decorator
