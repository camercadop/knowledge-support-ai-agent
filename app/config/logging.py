import logging
from typing import Literal

import structlog

from app.config.settings import settings


def configure_logging(mode: Literal["api", "cli"] = "api") -> None:
    """Configure structlog as the logging backend for the entire application.

    In CLI mode the output is always a human-friendly ConsoleRenderer regardless
    of LOG_FORMAT. In API mode the renderer is controlled by LOG_FORMAT.
    """
    api_processors: list[structlog.types.Processor] = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]
    cli_processors: list[structlog.types.Processor] = [
        structlog.stdlib.add_log_level,
    ]
    shared_processors = cli_processors if mode == "cli" else api_processors

    if mode == "cli":
        renderer: structlog.types.Processor = structlog.dev.ConsoleRenderer(
            level_styles={
                "debug": "\x1b[34m",  # blue
                "info": "\x1b[32m",  # green
                "warning": "\x1b[33m",  # yellow
                "error": "\x1b[31m",  # red
                "critical": "\x1b[1;31m",  # bold red
            },
            exception_formatter=structlog.dev.plain_traceback,
        )
    elif settings.log_format == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

    logging.basicConfig(
        level=logging.INFO,
        handlers=[logging.StreamHandler()],
    )
    logging.getLogger("app").setLevel(settings.log_level.upper())

    logging.getLogger().handlers[0].setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processors=[
                *(
                    [structlog.stdlib.ProcessorFormatter.remove_processors_meta]
                    if mode == "cli"
                    else []
                ),
                *shared_processors,
                renderer,
            ],
        )
    )
