# analytics

This sub-package contains everything belonging to the analytics domain: models, ports, and use cases.

## Structure

- `models/` — infrastructure-free dataclasses used as return types by repository ports
  - `rag_interaction_log.py` — `RagInteractionLog`
- `ports/` — abstract interfaces the use cases depend on
  - `repositories/rag_interaction_log.py` — `AbstractRagInteractionLogRepository`
- `use_cases/` — one module per user-facing action
  - `export_rag_interactions.py` — `ExportRagInteractions`

## Use Cases

### ExportRagInteractions

Returns all recorded RAG interaction logs for export. Delegates directly to the repository via `UnitOfWork`.
