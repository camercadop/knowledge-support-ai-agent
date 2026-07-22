# mock

This sub-package provides in-memory stubs for AI ports. Use these in tests to avoid real API calls and to keep the test suite fast and deterministic.

## Stubs

- `MockChatModel` — returns a fixed reply and token total configured at construction
- `MockEmbeddingModel` — returns a zero vector of configurable dimensions
- `MockToolRegistry` — executes handlers registered at construction; use when a test exercises a code path that invokes tools and needs predictable results
