# Application Services

A service is a class that encapsulates shared application-layer logic that does not belong to a single use case. It orchestrates ports but contains no infrastructure calls directly, and is consumed by multiple use cases or would bloat a use case if inlined.

The distinction from a use case is that a service has no entry-point semantics — it does not represent a user-facing action, it is a collaborator.

## Modules

- `chunk_retriever` — Wraps the `VectorStore` port with post-retrieval quality controls: deduplication, chunk capping, and token budget enforcement.
