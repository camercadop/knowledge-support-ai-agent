import uuid
from dataclasses import dataclass

from app.application.shared.events.domain_event import DomainEvent
from app.application.support.ports.vector_store import SearchResult


@dataclass(frozen=True)
class QuestionAnswered(DomainEvent):
    """Raised after a chat turn completes and both messages are persisted.

    Attributes:
        conversation_id: UUID of the conversation this turn belongs to.
        question: Raw user message text.
        answer: Assistant reply text.
        model_used: LLM model identifier used to generate the answer.
        chunks: Retrieved chunks as a list of dicts, or None if no context was used.
        prompt_tokens: Number of tokens in the prompt, or None.
        completion_tokens: Number of tokens in the completion, or None.
    """

    conversation_id: uuid.UUID
    question: str
    answer: str
    model_used: str
    chunks: list[SearchResult] | None
    prompt_tokens: int | None
    completion_tokens: int | None
