# application

This package contains the use cases of the system. Each sub-package groups the services for one feature area. A service receives plain inputs, coordinates the repositories and external clients it needs, owns the transaction boundary, and returns plain values to the API layer. No HTTP or ORM details leak into this layer.

## Sub-packages

- `chat/` — handles a full chat turn: contact and conversation resolution, history retrieval, LLM call, and message persistence
