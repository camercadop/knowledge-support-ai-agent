import uuid
from dataclasses import dataclass

from app.application.shared.events.domain_event import DomainEvent


@dataclass(frozen=True)
class ContextCompressed(DomainEvent):
    """Raised after context compression is applied during retrieval.

    Attributes:
        conversation_id: UUID of the conversation this retrieval belongs to,
            or None when compression occurs outside a conversation context.
        strategy: Identifier of the compression strategy applied.
        compression_ratio: Ratio of compressed tokens to original tokens (0.0-1.0).
        original_chunk_count: Number of chunks before compression.
        compressed_chunk_count: Number of chunks after compression.
    """

    conversation_id: uuid.UUID | None
    strategy: str
    compression_ratio: float
    original_chunk_count: int
    compressed_chunk_count: int
