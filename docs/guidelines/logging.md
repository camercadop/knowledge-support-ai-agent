# Logging Guidelines

This document defines the logging conventions for the project.

## Setup

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

## What Not to Log

- Passwords, tokens, or secrets.
- Full request or response bodies.
