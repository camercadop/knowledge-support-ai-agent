# application

This package contains the use cases of the system, organized by domain. Each domain sub-package owns its models, ports, services, and use cases. No HTTP or ORM details leak into this layer.

## Sub-packages

- `support/` — support domain: chat turn orchestration, document ingestion, and history management
- `analytics/` — analytics domain: RAG interaction log export
- `shared/` — cross-domain utilities: base ports, event infrastructure, and security logging
