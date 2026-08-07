# mock

This sub-package provides in-memory stubs for AI ports. Use these in tests to avoid real API calls and to keep the test suite fast and deterministic.

## Stubs

- `MockChatModel` — returns a fixed reply and token total configured at construction
- `MockEmbeddingModel` — returns a unit vector of configurable dimensions (first element `1.0`, rest `0.0`)
- `MockToolRegistry` — executes handlers registered at construction; use when a test exercises a code path that invokes tools and needs predictable results
