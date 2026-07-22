# ai

This package contains adapters for AI providers. Each sub-package implements one or more ports defined in `application/ports/` and isolates all provider-specific SDK imports so the rest of the codebase never depends on them directly.

## Sub-packages

- `chat/` — `ChatModel` implementation backed by the OpenAI Responses API
- `embeddings/` — `EmbeddingModel` implementation backed by the OpenAI Embeddings API
- `mock/` — in-memory stubs used in tests to avoid real API calls
- `tools/` — tool registry, `@tool` decorator, and all tool implementations available to the LLM
