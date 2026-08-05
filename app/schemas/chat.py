import re
import uuid

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """Payload for sending a chat message."""

    phone: str = Field(max_length=15)
    message: str = Field(min_length=1, max_length=4096)
    metadata_filters: dict[str, str] | None = None

    @field_validator("phone")
    @classmethod
    def sanitize_phone(cls, v: str) -> str:
        v = v.replace("\n", " ").replace("\r", " ")
        if not re.match(r"^\+[1-9]\d{1,14}$", v):
            raise ValueError(
                "Phone number must be in E.164 format (e.g. +1234567890)"
            )
        return v


class ChunkReference(BaseModel):
    """Metadata for a single knowledge chunk included in the RAG context."""

    chunk_id: uuid.UUID
    document_id: uuid.UUID
    score: float
    document_title: str
    source: str | None


class ChatResponse(BaseModel):
    """Response returned after processing a chat message."""

    reply: str
    chunks: list[ChunkReference] | None = None
