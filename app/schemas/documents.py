import uuid

from pydantic import BaseModel, Field, field_validator


class DocumentIngestRequest(BaseModel):
    """Payload for ingesting a document into the knowledge base."""

    title: str = Field(min_length=1, max_length=255)
    source: str | None = None
    content: str = Field(min_length=1)

    @field_validator("title")
    @classmethod
    def sanitize_title(cls, v: str) -> str:
        """Strip newline characters from the title to prevent log injection."""
        return v.replace("\n", " ").replace("\r", " ")


class DocumentIngestResponse(BaseModel):
    """Response returned after a document is successfully ingested."""

    id: uuid.UUID
    title: str
    source: str | None
