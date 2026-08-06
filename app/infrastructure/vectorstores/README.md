# vectorstores

This sub-package implements the `VectorStore` port for similarity search over document chunk embeddings.

## Modules

- `pgvector/store.py` — `PgVectorStore`; implements `upsert` and `search` using pgvector cosine distance via SQLAlchemy. Delegates search execution entirely to the injected `SearchStrategy`.
- `fake/store.py` — `FakeVectorStore`; in-memory implementation for tests and local development. Computes cosine distance directly in Python. Not suitable for production.
- `search_strategies/registry.py` — `@search_strategy` decorator, global registry, and `get_search_strategy` factory. Implementations register themselves by mode at import time.
- `search_strategies/strategies.py` — `VectorSearchStrategy` (pure cosine distance) and `HybridSearchStrategy` (vector + FTS fused via RRF), each with its own `SearchContext` subclass.
