import json
import logging
from typing import Any

import boto3

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


def _to_bedrock_messages(messages: list[ChatMessage]) -> list[dict[str, Any]]:
    """Convert ChatMessage value objects to Bedrock Converse API message dicts.

    Skips system messages — those are passed separately via the ``system`` parameter.

    Args:
        messages: Ordered list of ChatMessage value objects.

    Returns:
        List of message dicts accepted by the Bedrock Converse API.
    """
    return [
        {"role": m.role.value, "content": [{"text": m.content}]}
        for m in messages
        if m.role not in (Role.SYSTEM, Role.DEVELOPER)
    ]


def _to_bedrock_tool(definition: ToolDefinition) -> dict[str, Any]:
    """Convert a ToolDefinition to a Bedrock Converse API tool dict.

    Args:
        definition: The tool definition to convert.

    Returns:
        A tool dict suitable for the Bedrock Converse API.
    """
    required = [p.name for p in definition.parameters if p.required]
    properties: dict[str, Any] = {
        p.name: {"type": p.type, "description": p.description}
        for p in definition.parameters
    }
    return {
        "toolSpec": {
            "name": definition.name,
            "description": definition.description,
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                }
            },
        }
    }


@llm_provider("bedrock", "chat")
class BedrockChatModel(ChatModel):
    """ChatModel implementation backed by the AWS Bedrock Converse API."""

    @classmethod
    def build_settings(cls, settings: object) -> ChatModelSettings:
        """Build ChatModelSettings from application config for the Bedrock provider.

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
            provider_options=settings.chat_provider_options,
        )

    def __init__(
        self, prompt_builder: PromptBuilder, settings: ChatModelSettings | None
    ) -> None:
        """Initialize the Bedrock runtime client and prompt builder.

        Args:
            prompt_builder: Assembles the full message list before each API call.
            settings: Configuration for the Bedrock client and model.
        """
        region = (
            settings.provider_options.get("region", "us-east-1")
            if settings
            else "us-east-1"
        )
        self._client = boto3.client("bedrock-runtime", region_name=region)
        self._settings = settings
        self._prompt_builder = prompt_builder

    def generate(
        self,
        messages: list[ChatMessage],
        tool_registry: ToolRegistry | None = None,
        overrides: ChatModelOverrides | None = None,
    ) -> ChatResponse:
        """Send messages to the Bedrock Converse API and return the assistant reply.

        Extracts system messages and passes them via the ``system`` parameter.
        Runs a tool-use loop until the model produces a final text reply.

        Args:
            messages: Ordered list of ChatMessage value objects.
            tool_registry: Optional registry of tools the model may invoke.
            overrides: Per-call model, max_tokens, and temperature values.

        Returns:
            A ChatResponse with the assistant reply and token usage.
        """
        _overrides: ChatModelOverrides = overrides or {}
        model_id = _overrides.get(
            "model", self._settings.model if self._settings else ""
        )
        max_tokens = _overrides.get(
            "max_tokens", self._settings.max_tokens if self._settings else 1024
        )
        temperature = _overrides.get(
            "temperature", self._settings.temperature if self._settings else 1.0
        )

        system_text = " ".join(
            m.content for m in messages if m.role in (Role.SYSTEM, Role.DEVELOPER)
        )
        converse_messages = _to_bedrock_messages(messages)
        tools = (
            [_to_bedrock_tool(d) for d in tool_registry.list_definitions()]
            if tool_registry
            else []
        )

        logger.info("Calling Bedrock with %s messages", len(converse_messages))
        total_tokens = 0
        input_tokens = 0
        output_tokens = 0

        while True:
            kwargs: dict[str, Any] = {
                "modelId": model_id,
                "messages": converse_messages,
                "inferenceConfig": {
                    "maxTokens": max_tokens,
                    "temperature": float(temperature),
                },
            }
            if system_text:
                kwargs["system"] = [{"text": system_text}]
            if tools:
                kwargs["toolConfig"] = {"tools": tools}

            response = self._client.converse(**kwargs)

            usage = response.get("usage", {})
            total_tokens += usage.get("totalTokens", 0)
            input_tokens += usage.get("inputTokens", 0)
            output_tokens += usage.get("outputTokens", 0)

            output_message = response["output"]["message"]
            stop_reason = response.get("stopReason", "")

            if stop_reason != "tool_use":
                text = "".join(
                    block["text"]
                    for block in output_message["content"]
                    if "text" in block
                )
                logger.info("Bedrock response received, total_tokens=%s", total_tokens)
                logger.debug("Bedrock output: %s", text)
                return ChatResponse(
                    message=ChatMessage(role=Role.ASSISTANT, content=text),
                    usage=TokenUsage(
                        total=total_tokens or None,
                        input_tokens=input_tokens or None,
                        output_tokens=output_tokens or None,
                    ),
                    model_used=model_id,
                )

            converse_messages.append(dict(output_message))
            tool_results: list[dict[str, Any]] = []
            for block in output_message["content"]:
                if "toolUse" not in block:
                    continue
                tool_use = block["toolUse"]
                tool_name = tool_use["name"]
                arguments = tool_use["input"]
                tool_use_id = tool_use["toolUseId"]
                logger.info("Tool call: %s args=%s", tool_name, arguments)
                result = tool_registry.execute(tool_name, arguments)  # type: ignore[union-attr]
                logger.info("Tool result for %s: %s", tool_name, result)
                tool_results.append(
                    {
                        "toolUseId": tool_use_id,
                        "content": [{"text": json.dumps(result)}],
                    }
                )
            converse_messages.append(
                {"role": "user", "content": [{"toolResult": r} for r in tool_results]}
            )
