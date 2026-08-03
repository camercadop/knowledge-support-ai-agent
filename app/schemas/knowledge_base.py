import uuid

from pydantic import BaseModel, Field, field_validator


class KnowledgeBaseCreateRequest(BaseModel):
    """Payload for creating a knowledge base."""

    name: str = Field(min_length=1, max_length=255)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """Strip newline characters from the name to prevent log injection."""
        return v.replace("\n", " ").replace("\r", " ")


class KnowledgeBaseUpdateRequest(BaseModel):
    """Payload for partially updating a knowledge base."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str | None) -> str | None:
        """Strip newline characters from the name to prevent log injection."""
        if v is None:
            return v
        return v.replace("\n", " ").replace("\r", " ")



class KnowledgeBaseResponse(BaseModel):
    """Response returned after a knowledge base is created or retrieved."""

    id: uuid.UUID
    name: str
    description: str | None
