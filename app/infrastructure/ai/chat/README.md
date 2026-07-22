# chat

This sub-package implements the `ChatModel` port for the OpenAI Responses API.

## Modules

- `openai.py` — `OpenAIChatModel`; converts `ChatMessage` value objects to `EasyInputMessageParam`, calls `client.responses.create`, handles the tool-calling loop, and returns a `ChatResponse`. Prompt assembly is delegated to the injected `PromptBuilder`.
