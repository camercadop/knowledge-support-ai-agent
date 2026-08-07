# core

Cross-cutting infrastructure utilities that do not belong to a specific integration.

## Modules

- `settings.py` — `SettingsResolverAdapter`, `resolve_setting`, and `resolve_settings_batch`.

## SettingsResolverAdapter

Implements the `SettingsResolver` port from `app/application/support/ports/settings_resolver.py`. Resolves settings keys against the knowledge base config table, falling back to the global `Settings` value when no KB override is present.

KB config entries are loaded once per KB per TTL window (default 300 s) via a `TTLCache` and cast to the type declared on `Settings` at read time. Cast failures fall back to the global value with a warning log.
