# ai

This package contains adapters for AI providers. Each sub-package implements one or more ports defined in `application/ports/` and isolates all provider-specific SDK imports so the rest of the codebase never depends on them directly.

## Provider Registry

`registry.py` provides the `@llm_provider` decorator and the `get_chat_model` / `get_embedding_model` factory functions. Implementations self-register by decorating their class with `@llm_provider(name, model_type)`. The factories auto-discover all modules in the relevant packages on first call and return the class registered for the requested provider name.

## Sub-packages

- `chat/` — `ChatModel` implementations: `OpenAIChatModel` (OpenAI Responses API), `OllamaChatModel` (Ollama Chat Completions API), `BedrockChatModel` (AWS Bedrock)
- `chunking/` — `ChunkStrategy` implementations: fixed-size, recursive, and markdown-aware
- `embeddings/` — `EmbeddingModel` implementations: `OpenAIEmbeddingModel`, `OllamaEmbeddingModel`, `BedrockEmbeddingModel`
- `history_policies/` — `MessageRetentionPolicy` implementations: token limit, message count, role filter, and summarization
- `message_sanitizer/` — `MessageSanitizer` adapters: `RegexMessageSanitizer` (`regex.py`) and `CompositeSanitizer` (`base.py`)
- `mock/` — in-memory stubs used in tests to avoid real API calls
- `prompt_builder/` — `PromptBuilder` implementations: assembles the provider-agnostic message list including system prompt and retrieved context
- `tools/` — tool registry, `@tool` decorator, and all tool implementations available to the LLM
