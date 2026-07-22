# chat

This sub-package implements the `ChatModel` port using the OpenAI Responses API.

## Modules

- `openai.py` — `OpenAIChatModel`; prepends a system prompt with grounding instructions, converts `ChatMessage` value objects to `EasyInputMessageParam`, calls `client.responses.create`, and returns a `ChatResponse`. When retrieved context is available, the model is instructed to answer only from the provided excerpts. When no context is available, the model is instructed to tell the user it does not have enough information rather than fabricate an answer.
