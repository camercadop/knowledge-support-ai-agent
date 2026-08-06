# search_strategies

Pluggable retrieval strategies for `PgVectorStore.search`.

Each strategy encapsulates one retrieval mode end-to-end: it builds a typed context object from the call-site inputs and executes the corresponding query against the database.

## Modules

- `registry.py` — `@search_strategy(mode=...)` decorator, global registry, and `get_search_strategy` factory. Implementations self-register at import time. The container imports `strategies` to trigger registration before calling `get_search_strategy`.
- `strategies.py` — `VectorSearchStrategy` (pure cosine distance) and `HybridSearchStrategy` (vector + PostgreSQL full-text search fused via RRF). `HybridSearchStrategy` uses `HybridSearchContext`, a `SearchContext` subclass that carries `fts_language` and `rrf_k` set from constructor-injected settings.

## Adding a new strategy

1. Create a subclass of `SearchStrategy` in `strategies.py` (or a new module).
2. If the strategy needs extra per-call inputs beyond `SearchContext`, define a frozen dataclass subclass of `SearchContext` and return it from `build_context`.
3. Decorate the class with `@search_strategy(mode="your_mode")`.
4. Add the corresponding `retrieval_mode` value to `Settings` and document it in the configuration table.
