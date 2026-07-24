# infrastructure

This package contains adapters for every external system the application depends on. Each sub-package isolates one integration behind a stable internal interface, so the rest of the codebase never imports third-party SDKs directly. Swapping or mocking an external dependency only requires changes inside the relevant sub-package.

## Sub-packages

- `database/` — SQLAlchemy engine, session factory, ORM models, repositories, and migrations
- `ai/` — chat and embedding provider adapters
- `vectorstores/` — vector store implementations (pgvector)
- `observability/` — OTel instrumentation utilities and domain-scoped metric definitions
