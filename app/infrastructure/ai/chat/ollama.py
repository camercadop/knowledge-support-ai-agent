import json
import logging
from typing import Any

from openai import OpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCallParam,
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
    ChatCompletionUserMessageParam,
)
from openai.types.shared_params import FunctionDefinition

from app.application.support.ports.chat_model import (
    ChatMessage,
    ChatModel,
    ChatModelOverrides,
    ChatModelSettings,
    ChatResponse,
    Role,
    TokenUsage,
)
from app.application.support.ports.prompt_builder import PromptBuilder
from app.application.support.ports.tool_registry import ToolDefinition, ToolRegistry
from app.infrastructure.ai.registry import llm_provider

logger = logging.getLogger(__name__)


def _to_chat_completion_message(message: ChatMessage) -> ChatCompletionMessageParam:
    """Convert a ChatMessage to an OpenAI Chat Completions message param.

    Maps DEVELOPER role to ``system`` since the Chat Completions API does not
    have a developer role.

    Args:
        message: The ChatMessage value object to convert.

    Returns:
        A typed ChatCompletionMessageParam dict.
    """
    role = "system" if message.role == Role.DEVELOPER else message.role.value
    if role == "user":
        return ChatCompletionUserMessageParam(role="user", content=message.content)
    if role == "assistant":
        return ChatCompletionAssistantMessageParam(
            role="assistant", content=message.content
        )
    return {"role": role, "content": message.content}  # type: ignore[misc, return-value]


def _to_tool_param(definition: ToolDefinition) -> ChatCompletionToolParam:
    """Convert a ToolDefinition to an OpenAI Chat Completions tool param.

    Args:
        definition: The tool definition to convert.

    Returns:
        A ChatCompletionToolParam suitable for the Chat Completions API.
    """
    required = [p.name for p in definition.parameters if p.required]
    properties: dict[str, Any] = {
        p.name: {"type": p.type, "description": p.description}
        for p in definition.parameters
    }
    return ChatCompletionToolParam(
        type="function",
        function=FunctionDefinition(
            name=definition.name,
            description=definition.description,
            parameters={
                "type": "object",
                "properties": properties,
                "required": required,
            },
        ),
    )


@llm_provider("ollama", "chat")
class OllamaChatModel(ChatModel):
    """ChatModel implementation backed by the Ollama Chat Completions API.

    Uses the OpenAI-compatible ``/v1/chat/completions`` endpoint exposed by
    Ollama. Supports tool calling for models that declare function-calling
    capability (e.g. llama3.2, mistral-nemo).
    """

    @classmethod
    def build_settings(cls, settings: object) -> ChatModelSettings:
        """Build ChatModelSettings from application config for the Ollama provider.

        Args:
            settings: The application Settings instance.

        Returns:
            A ChatModelSettings instance populated from application settings.
        """
        from app.config.settings import Settings

        assert isinstance(settings, Settings)
        return ChatModelSettings(
            model=settings.chat_model,
            max_tokens=settings.chat_max_tokens,
            temperature=settings.chat_temperature,
            api_key=settings.chat_api_key,
            base_url=settings.chat_base_url,
            provider_options=settings.chat_provider_options,
        )

    def __init__(
        self, prompt_builder: PromptBuilder, settings: ChatModelSettings | None
    ) -> None:
        """Initialize the OpenAI client pointed at the Ollama endpoint.

        Args:
            prompt_builder: Assembles the full message list before each API call.
            settings: Configuration for the Ollama client and model. ``base_url``
                must point to the Ollama server (e.g. ``http://localhost:11434/v1``).
        """
        self._client = OpenAI(
            api_key=settings.api_key if settings else "ollama",
            base_url=settings.base_url if settings else "http://localhost:11434/v1",
        )
        self._settings = settings
        self._prompt_builder = prompt_builder

    def generate(
        self,
        messages: list[ChatMessage],
        tool_registry: ToolRegistry | None = None,
        overrides: ChatModelOverrides | None = None,
    ) -> ChatResponse:
        """Send messages to the Ollama Chat Completions API and return the reply.

        Runs a tool-use loop until the model produces a final text reply without
        any tool calls.

        Args:
            messages: Ordered list of ChatMessage value objects.
            tool_registry: Optional registry of tools the model may invoke.
            overrides: Per-call model, max_tokens, and temperature values.

        Returns:
            A ChatResponse with the assistant reply and token usage.
        """
        _overrides: ChatModelOverrides = overrides or {}
        model = _overrides.get("model", self._settings.model if self._settings else "")
        max_tokens = _overrides.get(
            "max_tokens", self._settings.max_tokens if self._settings else 1024
        )
        temperature = _overrides.get(
            "temperature", self._settings.temperature if self._settings else 1.0
        )

        conversation: list[ChatCompletionMessageParam] = [
            _to_chat_completion_message(m) for m in messages
        ]
        tools = (
            [_to_tool_param(d) for d in tool_registry.list_definitions()]
            if tool_registry
            else []
        )

        logger.info("Calling Ollama with %s messages", len(conversation))
        total_tokens = 0
        input_tokens = 0
        output_tokens = 0

        while True:
            kwargs: dict[str, Any] = {
                "model": model,
                "messages": conversation,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            if tools:
                kwargs["tools"] = tools

            response = self._client.chat.completions.create(**kwargs)

            if response.usage:
                total_tokens += response.usage.total_tokens or 0
                input_tokens += response.usage.prompt_tokens or 0
                output_tokens += response.usage.completion_tokens or 0

            choice = response.choices[0]
            assistant_message = choice.message

            if not assistant_message.tool_calls:
                content = assistant_message.content or ""
                logger.info("Ollama response received, total_tokens=%s", total_tokens)
                logger.debug("Ollama output: %s", content)
                return ChatResponse(
                    message=ChatMessage(role=Role.ASSISTANT, content=content),
                    usage=TokenUsage(
                        total=total_tokens or None,
                        input_tokens=input_tokens or None,
                        output_tokens=output_tokens or None,
                    ),
                    model_used=model,
                )

            tool_call_params: list[ChatCompletionMessageToolCallParam] = [
                ChatCompletionMessageToolCallParam(
                    id=tc.id,
                    type="function",
                    function={
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                )
                for tc in assistant_message.tool_calls
            ]
            conversation.append(
                ChatCompletionAssistantMessageParam(
                    role="assistant",
                    content=assistant_message.content or "",
                    tool_calls=tool_call_params,
                )
            )

            for tc in assistant_message.tool_calls:
                arguments = json.loads(tc.function.arguments)
                logger.info("Tool call: %s args=%s", tc.function.name, arguments)
                result = tool_registry.execute(tc.function.name, arguments)  # type: ignore[union-attr]
                logger.info("Tool result for %s: %s", tc.function.name, result)
                tool_message: ChatCompletionToolMessageParam = (
                    ChatCompletionToolMessageParam(
                        role="tool",
                        tool_call_id=tc.id,
                        content=json.dumps(result),
                    )
                )
                conversation.append(tool_message)
