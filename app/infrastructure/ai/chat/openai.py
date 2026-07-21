import logging

from openai import OpenAI
from openai.types.responses import EasyInputMessageParam

from app.application.ports.chat_model import (
    ChatMessage,
    ChatModel,
    ChatResponse,
    Role,
    TokenUsage,
)
from app.config.settings import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a helpful support assistant. Answer questions clearly and concisely."
)

_ALLOWED_ROLES = {"user", "assistant", "system", "developer"}


def _to_input(
    messages: list[ChatMessage],
    context: str | None = None,
) -> list[EasyInputMessageParam]:
    """Convert ChatMessage value objects to typed EasyInputMessageParam entries.

    Prepends the system prompt, optionally extended with retrieved context.
    Skips entries with unrecognised roles.

    Args:
        messages: Ordered list of ChatMessage value objects.
        context: Optional retrieved knowledge chunks to append to the system prompt.
    """
    system_content = (
        f"{SYSTEM_PROMPT}\n\nUse the following knowledge base excerpts to answer:\n{context}"
        if context
        else SYSTEM_PROMPT
    )
    result: list[EasyInputMessageParam] = [
        EasyInputMessageParam(role="system", content=system_content)
    ]
    for m in messages:
        if m.role.value in _ALLOWED_ROLES:
            result.append(
                EasyInputMessageParam(
                    role=m.role.value,
                    content=m.content,
                )
            )
    return result


class OpenAIChatModel(ChatModel):
    """ChatModel implementation backed by the OpenAI Responses API."""

    def __init__(self) -> None:
        """Initialize the OpenAI client from application settings."""
        self._client = OpenAI(
            api_key=settings.chat_api_key,
            base_url=settings.chat_base_url,
        )

    def generate(
        self, messages: list[ChatMessage], context: str | None = None
    ) -> ChatResponse:
        """Send messages to the OpenAI Responses API and return the reply.

        Prepends the system prompt, merged with retrieved context when provided.
        Skips messages with unrecognised roles.

        Args:
            messages: Ordered list of ChatMessage value objects.
            context: Optional retrieved knowledge to merge into the system prompt.
        """
        input_messages = _to_input(messages, context)
        logger.info("Calling LLM with %s messages", len(messages))
        logger.debug("LLM input messages: %s", input_messages)
        response = self._client.responses.create(
            model=settings.chat_model,
            input=input_messages,  # type: ignore[arg-type]
            max_output_tokens=settings.chat_max_tokens,
        )
        total_tokens = response.usage.total_tokens if response.usage else None
        logger.info("LLM response received, total_tokens=%s", total_tokens)
        logger.debug("LLM output: %s", response.output_text)
        return ChatResponse(
            message=ChatMessage(role=Role.ASSISTANT, content=response.output_text),
            usage=TokenUsage(total=total_tokens),
        )
