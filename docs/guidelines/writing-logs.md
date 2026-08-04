# Logging Guidelines

This document defines the logging conventions for the project.

## Setup

Logging is configured globally in `app/main.py` using `structlog` with stdlib integration. Two env vars control the behaviour:

- `LOG_LEVEL` — standard Python log level (default: `INFO`)
- `LOG_FORMAT` — `text` for colored console output (default), `json` for structured JSON output (production)

Every module that emits log output must declare a module-level logger:

```python
import logging

logger = logging.getLogger(__name__)
```

## Log Levels

- `logger.info` — normal, expected events.
- `logger.warning` — security-relevant or unexpected events.
- `logger.error` — unhandled exceptions.

## Formatting

Always use `%s`-style formatting — never f-strings in log calls.

```python
# correct
logger.info("Processing message %s", message_id)

# wrong
logger.info(f"Processing message {message_id}")
```

## Security Events

Security-relevant events (rejected messages, rate limit hits, oversized requests) must use `log_security_event()` from `app/application/shared/security/logger.py` instead of a plain logger call. This ensures all security audit entries share a consistent structure and are routed through the `app.security` logger.

```python
from app.application.shared.security.logger import log_security_event

log_security_event("support.message_rejected", phone=phone, reason=exc.reason)
```

The `level` parameter defaults to `"warning"`. Use `"info"` for informational events and `"error"` for critical failures.

## What Not to Log

- Passwords, tokens, or secrets.
- Full request or response bodies.
