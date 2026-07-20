# config

This package centralizes all application configuration. Settings are declared as a `pydantic-settings` model and populated from environment variables or a `.env` file at startup. A single `settings` singleton is instantiated here and imported directly by any module that needs a configuration value.

## Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DATABASE_URL` | `str` | — | PostgreSQL connection string |
| `OPENAI_API_KEY` | `str` | — | OpenAI API key |
| `OPENAI_MODEL` | `str` | `gpt-4o-mini` | Model name |
| `OPENAI_BASE_URL` | `str \| None` | `None` | Optional base URL override |
| `OPENAI_EMBEDDING_MODEL` | `str` | `text-embedding-3-small` | Embedding model name |
| `EMBEDDING_DIMENSIONS` | `int` | `1536` | Embedding vector dimensions |
| `WHATSAPP_TOKEN` | `str` | — | WhatsApp Cloud API token |
| `WHATSAPP_VERIFY_TOKEN` | `str` | — | Webhook verification token |
| `LOG_LEVEL` | `str` | `INFO` | Python log level |
| `LOG_FORMAT` | `str` | `text` | Output format: `text` for colored console, `json` for structured production logs |

Values are read from the environment or a `.env` file at startup. The `settings` singleton is imported directly by other modules.

## Modules

- `settings.py` — `Settings` class and the `settings` singleton
- `logging.py` — `configure_logging()` function; call once at application startup to configure structlog as the logging backend
