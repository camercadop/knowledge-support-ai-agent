# chat

This sub-package implements the `ChatModel` port using the OpenAI Responses API.

## Modules

- `openai.py` — `OpenAIChatModel`; prepends a system prompt, converts `ChatMessage` value objects to `EasyInputMessageParam`, calls `client.responses.create`, and returns a `ChatResponse`
