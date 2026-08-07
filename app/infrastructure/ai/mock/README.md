# mock

This sub-package provides in-memory stubs for AI ports. Use these in tests to avoid real API calls and to keep the test suite fast and deterministic. Both stubs self-register via `@llm_provider` so they are discoverable under the `mock` provider name.

## Stubs

- `MockChatModel` — returns a fixed reply and token total configured at construction via `reply` and `token_total` kwargs. Accepts `prompt_builder` and `settings` to satisfy the `ChatModel` constructor contract but ignores them.
- `MockEmbeddingModel` — returns a unit vector of configurable length (first element `1.0`, rest `0.0`). Accepts `settings` to satisfy the `EmbeddingModel` constructor contract and an optional `dimensions` kwarg (default `3`) to control the vector length.
- `MockToolRegistry` — executes handlers registered at construction; use when a test exercises a code path that invokes tools and needs predictable results.
