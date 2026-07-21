import logging
from typing import get_args

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

_ALLOWED_ROLES = set(
    get_args(EasyInputMessageParam.__annotations__["role"])
)


def _to_input(
    messages: list[ChatMessage],
) -> list[EasyInputMessageParam]:
    """Convert ChatMessage value objects to typed EasyInputMessageParam entries.

    Prepends the system prompt. Skips entries with unrecognised roles.
    """
    result: list[EasyInputMessageParam] = [
        EasyInputMessageParam(role="system", content=SYSTEM_PROMPT)
    ]
    for m in messages:
        if m.role in _ALLOWED_ROLES:
            result.append(
                EasyInputMessageParam(
                    role=m.role,  # type: ignore[typeddict-item]
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

    def generate(self, messages: list[ChatMessage]) -> ChatResponse:
        """Send messages to the OpenAI Responses API and return the reply.

        Prepends the system prompt automatically. Skips messages with
        unrecognised roles.
        """
        logger.info("Calling LLM with %s messages", len(messages))
        response = self._client.responses.create(
            model=settings.chat_model,
            input=_to_input(messages),  # type: ignore[arg-type]
        )
        total_tokens = response.usage.total_tokens if response.usage else None
        logger.info("LLM response received, total_tokens=%s", total_tokens)
        return ChatResponse(
            message=ChatMessage(role=Role.ASSISTANT, content=response.output_text),
            usage=TokenUsage(total=total_tokens),
        )
