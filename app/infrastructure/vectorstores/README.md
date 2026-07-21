# vectorstores

This sub-package implements the `VectorStore` port for similarity search over document chunk embeddings.

## Modules

- `pgvector/store.py` — `PgVectorStore`; implements `upsert` and `search` using pgvector cosine distance via SQLAlchemy. `search` returns a list of `SearchResult` ordered from most to least similar.
