import uuid
from datetime import datetime

from pydantic import BaseModel


class DocumentChunk(BaseModel):
    """Represents a text chunk of a document in the application layer."""

    chunk_id: uuid.UUID
    document_id: uuid.UUID
    score: float


class RagInteractionLogResponse(BaseModel):
    """Response schema for a single RAG interaction log entry."""

    id: uuid.UUID
    conversation_id: uuid.UUID
    question: str
    answer: str
    model_used: str
    chunks: list[DocumentChunk] | None
    prompt_tokens: int | None
    completion_tokens: int | None
    created_at: datetime
