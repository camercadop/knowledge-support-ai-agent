# chat

This sub-package implements the `ChatModel` port for the OpenAI Responses API.

## Modules

- `openai.py` — `OpenAIChatModel`; converts `ChatMessage` value objects to `EasyInputMessageParam`, calls `client.responses.create`, handles the tool-calling loop, and returns a `ChatResponse`. Prompt assembly is delegated to the injected `PromptBuilder`.

## Configuration

`OpenAIChatModel` is constructed with a `ChatModelSettings` dataclass holding the client-level options (`api_key`, `base_url`) and default model options (`model`, `max_tokens`, `temperature`). Per-call overrides are passed via `ChatModelOverrides` (a `TypedDict` defined in the `ChatModel` port) to `generate`. Any key present in `ChatModelOverrides` takes precedence over the `ChatModelSettings` default for that call.

## Tool-Calling Loop

When tools are registered, the model may invoke one or more tools before producing a final text reply. Each iteration appends the `function_call` output items and their `function_call_output` results directly to `input_messages`, then issues a new `responses.create` call with the full accumulated input. This avoids relying on `previous_response_id` for state, which is not reliably supported by all providers (e.g. Ollama). The loop exits when the model returns a turn with no tool calls.
