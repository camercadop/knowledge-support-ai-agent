import logging

import structlog

from app.config.settings import settings


def configure_logging() -> None:
    """Configure structlog as the logging backend for the entire application.

    Routes all stdlib logging.getLogger() callers through structlog's processor
    chain. Output format is controlled by the LOG_FORMAT env var: use "text" for
    colored console output (default) and "json" for structured production logs.
    """
    # Processors shared between structlog's own pipeline and the stdlib formatter,
    # ensuring both produce identical fields regardless of the entry point.
    shared_processors: list[structlog.types.Processor] = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if settings.log_format == "json":
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    # Configure structlog to hand off to stdlib so that logging.getLogger() callers
    # are routed through the same processor chain as structlog.get_logger() callers.
    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

    logging.basicConfig(
        level=settings.log_level.upper(),
        handlers=[logging.StreamHandler()],
    )

    # Replace the default stdlib formatter with structlog's ProcessorFormatter so
    # all stdlib log records are rendered through the same pipeline and renderer.
    logging.getLogger().handlers[0].setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processors=[*shared_processors, renderer],
        )
    )
