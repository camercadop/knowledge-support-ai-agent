# embeddings

This sub-package implements the `EmbeddingModel` port using the OpenAI Embeddings API.

## Modules

- `openai.py` — module-level `embed(text)` function; calls `client.embeddings.create` with the model and dimensions from settings and returns a flat list of floats suitable for storage in a pgvector column
