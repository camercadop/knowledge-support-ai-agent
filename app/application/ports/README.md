# ports

This package defines the abstract interfaces (ports) that the application layer depends on. No implementation details or third-party imports live here. Each port is an abstract base class that the infrastructure layer implements, keeping the application layer fully decoupled from external systems.

## Ports

- `chat_model.py` — `ChatModel`; contract for chat completion providers. Also defines `ChatMessage`, `ChatResponse`, `TokenUsage`, and `Role`
- `embedding_model.py` — `EmbeddingModel`; contract for text embedding providers
- `vector_store.py` — `VectorStore`; contract for vector store providers. Also defines `SearchResult`

## Sub-packages

- `repositories/` — one abstract repository per aggregate root
- `unit_of_work/` — one domain-scoped transactional boundary per bounded context
