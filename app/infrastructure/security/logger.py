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
    """Log a security event with structured fields.

    The security logger uses the ``app.security`` logger name so that
    security audit trails can be filtered and parsed independently from
    application logs. All extra fields are attached to the LogRecord via
    ``extra`` so that structured log backends can index them.

    Args:
        event: A short, machine-readable event name following the
            ``<namespace>.<event>`` convention
        level: Log level — ``"warning"`` (default), ``"info"``, or ``"error"``.
            Raises ``ValueError`` if an unsupported level is provided.
        **fields: Arbitrary keyword arguments that become structured
            fields on the log record.

    Raises:
        ValueError: If ``level`` is not one of the supported log levels.
    """
    if level not in _VALID_LEVELS:
        raise ValueError(f"level must be one of {sorted(_VALID_LEVELS)}, got {level!r}")

    getattr(security_logger, level)(
        "security event: %s",
        event,
        extra={"security_event": event, **fields},
    )
