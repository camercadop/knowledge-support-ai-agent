from typing import Literal, get_args

from openai import OpenAI
from openai.types.responses import EasyInputMessageParam

from app.config.settings import settings

SYSTEM_PROMPT = (
    "You are a helpful support assistant. Answer questions clearly and concisely."
)

_client = OpenAI(
    api_key=settings.openai_api_key,
    base_url=settings.openai_base_url,
)

_ALLOWED_ROLES = set(
    get_args(EasyInputMessageParam.__annotations__["role"])
)

Role = Literal["user", "assistant", "system", "developer"]


class LLMResponse:
    """Holds the text reply and token usage from an LLM call."""

    def __init__(self, content: str, total_tokens: int | None) -> None:
        """Initialize with the reply content and token count."""
        self.content = content
        self.total_tokens = total_tokens


def _to_input(
    messages: list[dict[str, str]],
) -> list[EasyInputMessageParam]:
    """Convert plain dicts to typed EasyInputMessageParam entries.

    Prepends the system prompt. Skips entries with unrecognised roles.
    """
    result: list[EasyInputMessageParam] = [
        EasyInputMessageParam(role="system", content=SYSTEM_PROMPT)
    ]
    for m in messages:
        role = m.get("role", "")
        if role in _ALLOWED_ROLES:
            result.append(
                EasyInputMessageParam(
                    role=role,  # type: ignore[typeddict-item]
                    content=m["content"],
                )
            )
    return result


def chat(messages: list[dict[str, str]]) -> LLMResponse:
    """Send a list of messages to the OpenAI Responses API and return the reply.

    Expects messages in OpenAI format: [{"role": "...", "content": "..."}].
    Prepends the system prompt automatically.
    """
    response = _client.responses.create(
        model=settings.openai_model,
        input=_to_input(messages),  # type: ignore[arg-type]
    )

    content = response.output_text
    total_tokens = response.usage.total_tokens if response.usage else None

    return LLMResponse(content=content, total_tokens=total_tokens)
