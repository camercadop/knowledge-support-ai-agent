# llm

This sub-package wraps the OpenAI APIs. It exposes a `chat` function for conversational completions and an `embed` function for generating vector embeddings. The application layer calls these without knowing any SDK details.

## Flow

```mermaid
flowchart
    ChatService -->|"chat(messages)"| openai_client
    openai_client -->|responses.create| OpenAI_API
    OpenAI_API -->|output_text, usage| openai_client
    openai_client -->|LLMResponse| ChatService

    Consumer -->|"embed(text)"| embeddings
    embeddings -->|embeddings.create| OpenAI_API
    OpenAI_API -->|embedding vector| embeddings
    embeddings -->|list[float]| Consumer
```

## Modules

- `openai_client.py` — `chat(messages)` function; prepends the system prompt, filters unknown roles, calls the API, and returns an `LLMResponse` with `content` and `total_tokens`
- `embeddings.py` — `embed(text)` function; calls the OpenAI embeddings API using `text-embedding-3-small` at 1536 dimensions and returns a `list[float]`
