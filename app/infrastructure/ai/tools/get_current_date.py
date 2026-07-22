from datetime import date
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
