import logging
from typing import Any, Literal

security_logger = logging.getLogger("app.security")

SecurityLogLevel = Literal["info", "warning", "error"]
_VALID_LEVELS: frozenset[str] = frozenset(SecurityLogLevel.__args__)  # type: ignore[attr-defined]


def log_security_event(
    event: str,
    *,
    level: SecurityLogLevel = "warning",
    **fields: Any,
) -> None:
    if level not in _VALID_LEVELS:
        raise ValueError(f"level must be one of {sorted(_VALID_LEVELS)}, got {level!r}")

    getattr(security_logger, level)(
        "security event: %s",
        event,
        extra={"security_event": event, **fields},
    )
