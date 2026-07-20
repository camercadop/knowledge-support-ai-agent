# Writing Settings

This document describes how to add and access application settings in this project.

## Purpose

Settings are defined in `app/config/settings.py` using `pydantic-settings`. They are loaded once at startup from environment variables and the `.env` file.

## Adding a New Setting

Add a field to the `Settings` class:

```python
class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # existing fields ...
    my_new_setting: str
    my_optional_setting: str | None = None
```

Then add the corresponding entry to `.env.example`:

```bash
MY_NEW_SETTING=
```

## Accessing Settings

Import the module-level singleton from anywhere in the application:

```python
from app.config.settings import settings

value = settings.my_new_setting
```

## Rules

- Required settings have no default value — startup fails fast if they are missing.
- Optional settings use `str | None = None` (never bare `None` without the union type).
- Never instantiate `Settings` outside of `app/config/settings.py`.
- Always keep `.env.example` in sync when adding or removing settings.
- Never log or expose setting values that contain secrets or tokens.
