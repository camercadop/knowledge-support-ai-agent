# embeddings

This sub-package implements the `EmbeddingModel` port for multiple providers. Each implementation self-registers via the `@llm_provider` decorator defined in `app/infrastructure/ai/registry.py`, making it discoverable by `get_embedding_model` at runtime.

## Modules

- `openai.py` — `OpenAIEmbeddingModel`; reads configuration from the module-level `settings` object, calls `client.embeddings.create` with the configured model and dimensions, and returns a flat list of floats suitable for storage in a pgvector column.
- `ollama.py` — `OllamaEmbeddingModel`; uses the OpenAI-compatible `/v1/embeddings` endpoint exposed by Ollama. Accepts `base_url` and optional `dimensions` from settings.
- `bedrock.py` — `BedrockEmbeddingModel`; invokes the AWS Bedrock runtime via `boto3`. Expects the model response to contain an `embedding` key (Amazon Titan Embed and Cohere Embed format).
