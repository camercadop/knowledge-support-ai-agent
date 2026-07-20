# llm

This sub-package wraps the OpenAI Responses API. It exposes a single `chat` function that the application layer calls without knowing any SDK details.

## Flow

```mermaid
flowchart
    ChatService -->|"chat(messages)"| openai_client
    openai_client -->|responses.create| OpenAI_API
    OpenAI_API -->|output_text, usage| openai_client
    openai_client -->|LLMResponse| ChatService
```

## Modules

- `openai_client.py` — `chat(messages)` function; prepends the system prompt, filters unknown roles, calls the API, and returns an `LLMResponse` with `content` and `total_tokens`
