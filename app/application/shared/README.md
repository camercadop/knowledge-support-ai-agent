# shared

Cross-domain application-layer utilities shared across all domains. Nothing in this package imports from infrastructure or any domain sub-package.

## Sub-packages

- `events/` — base event types, event publisher port, and event handler interface
- `ports/` — base repository and unit of work abstractions
- `use_cases/` — base CRUD use case
- `security/` — application-layer security utilities, usable across all domains without infrastructure dependencies
