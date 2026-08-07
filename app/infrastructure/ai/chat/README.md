# chat

This sub-package implements the `ChatModel` port for multiple providers. Each implementation self-registers via the `@llm_provider` decorator defined in `app/infrastructure/ai/registry.py`, making it discoverable by `get_chat_model` at runtime.

## Modules

- `openai.py` — `OpenAIChatModel`; converts `ChatMessage` value objects to `EasyInputMessageParam`, calls `client.responses.create`, handles the tool-calling loop, and returns a `ChatResponse`. Prompt assembly is delegated to the injected `PromptBuilder`.
- `ollama.py` — `OllamaChatModel`; uses the OpenAI-compatible `/v1/chat/completions` endpoint exposed by Ollama. Supports tool calling for models that declare function-calling capability (e.g. `llama3.2`, `mistral-nemo`).
- `bedrock.py` — `BedrockChatModel`; calls the AWS Bedrock Converse API via `boto3`. Supports tool calling for models that declare function-calling capability.

## Configuration

Each implementation is constructed with a `ChatModelSettings` instance holding the client-level options (`api_key`, `base_url`) and default model options (`model`, `max_tokens`, `temperature`). `build_settings` on each class maps the application `Settings` object to a `ChatModelSettings`. Per-call overrides are passed via `ChatModelOverrides` (a `TypedDict` defined in the `ChatModel` port) to `generate`. Any key present in `ChatModelOverrides` takes precedence over the `ChatModelSettings` default for that call.

## Tool-Calling Loop

When tools are registered, the model may invoke one or more tools before producing a final text reply. Each iteration appends the tool call outputs and their results to the conversation, then issues a new API call with the full accumulated input. The loop exits when the model returns a turn with no tool calls.
