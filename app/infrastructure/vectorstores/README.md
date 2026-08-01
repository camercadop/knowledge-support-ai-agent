# vectorstores

This sub-package implements the `VectorStore` port for similarity search over document chunk embeddings.

## Modules

- `pgvector/store.py` — `PgVectorStore`; implements `upsert` and `search` using pgvector cosine distance via SQLAlchemy. `search` joins the `documents` table to include `document_title` and `source` in each `SearchResult`.
- `fake/store.py` — `FakeVectorStore`; in-memory implementation for tests and local development. Computes cosine distance directly in Python. Not suitable for production.
