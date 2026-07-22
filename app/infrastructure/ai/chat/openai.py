import json
import logging
from typing import Any

from openai import OpenAI
from openai.types.responses import EasyInputMessageParam, FunctionToolParam

from app.application.ports.chat_model import (
    ChatMessage,
    ChatModel,
    ChatResponse,
    Role,
    TokenUsage,
)
from app.application.ports.prompt_builder import PromptBuilder
from app.application.ports.tool_registry import ToolDefinition, ToolRegistry
from app.config.settings import settings

logger = logging.getLogger(__name__)

_ALLOWED_ROLES = {"user", "assistant", "system", "developer"}


def _to_input(messages: list[ChatMessage]) -> list[EasyInputMessageParam]:
    """Convert ChatMessage value objects to typed EasyInputMessageParam entries.

    Skips entries with unrecognised roles.

    Args:
        messages: Ordered list of ChatMessage value objects.

    Returns:
        List of EasyInputMessageParam entries.
    """
    return [
        EasyInputMessageParam(role=m.role.value, content=m.content)
        for m in messages
        if m.role.value in _ALLOWED_ROLES
    ]


def _to_function_tool(definition: ToolDefinition) -> FunctionToolParam:
    """Convert a ToolDefinition to an OpenAI FunctionToolParam.

    Args:
        definition: The tool definition to convert.

    Returns:
        A FunctionToolParam suitable for the OpenAI Responses API.
    """
    required = [p.name for p in definition.parameters if p.required]
    properties: dict[str, Any] = {
        p.name: {"type": p.type, "description": p.description}
        for p in definition.parameters
    }
    return FunctionToolParam(
        type="function",
        name=definition.name,
        description=definition.description,
        strict=False,
        parameters={
            "type": "object",
            "properties": properties,
            "required": required,
        },
    )


class OpenAIChatModel(ChatModel):
    """ChatModel implementation backed by the OpenAI Responses API."""

    def __init__(self, prompt_builder: PromptBuilder) -> None:
        """Initialize the OpenAI client and prompt builder from application settings.

        Args:
            prompt_builder: Assembles the full message list before each API call.
        """
        self._client = OpenAI(
            api_key=settings.chat_api_key,
            base_url=settings.chat_base_url,
        )
        self._prompt_builder = prompt_builder

    def generate(
        self,
        messages: list[ChatMessage],
        tool_registry: ToolRegistry | None = None,
    ) -> ChatResponse:
        """Send messages to the OpenAI Responses API and return the assistant reply.

        Args:
            messages: Ordered list of ChatMessage value objects. Must already include
                the system message assembled by the injected PromptBuilder.
            tool_registry: Optional registry of tools the model may invoke in a
                loop until it produces a final text reply.

        Returns:
            A ChatResponse with the assistant reply and token usage.
        """
        input_messages: list[Any] = list(_to_input(messages))
        tools = (
            [_to_function_tool(d) for d in tool_registry.list_definitions()]
            if tool_registry
            else []
        )

        logger.info("Calling LLM with %s messages", len(messages))
        total_tokens = 0
        previous_response_id: str | None = None

        while True:
            kwargs: dict[str, Any] = {
                "model": settings.chat_model,
                "max_output_tokens": settings.chat_max_tokens,
            }
            if previous_response_id:
                kwargs["previous_response_id"] = previous_response_id
            else:
                kwargs["input"] = input_messages
            if tools:
                kwargs["tools"] = tools

            response = self._client.responses.create(**kwargs)

            if response.usage:
                total_tokens += response.usage.total_tokens or 0

            tool_calls = [
                item for item in response.output if item.type == "function_call"
            ]

            if not tool_calls:
                logger.info("LLM response received, total_tokens=%s", total_tokens)
                logger.debug("LLM output: %s", response.output_text)
                return ChatResponse(
                    message=ChatMessage(
                        role=Role.ASSISTANT,
                        content=response.output_text,
                    ),
                    usage=TokenUsage(total=total_tokens or None),
                )

            previous_response_id = response.id
            for call in tool_calls:
                arguments = json.loads(call.arguments)
                logger.info("Tool call: %s args=%s", call.name, arguments)
                result = tool_registry.execute(call.name, arguments)  # type: ignore[union-attr]
                logger.info("Tool result for %s: %s", call.name, result)
                input_messages.append(
                    {
                        "type": "function_call_output",
                        "call_id": call.call_id,
                        "output": result,
                    }
                )
