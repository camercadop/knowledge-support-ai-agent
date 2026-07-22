from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """Payload for sending a chat message."""

    phone: str
    message: str = Field(min_length=1, max_length=4096)

    @field_validator("phone")
    @classmethod
    def sanitize_phone(cls, v: str) -> str:
        return v.replace("\n", " ").replace("\r", " ")


class ChatResponse(BaseModel):
    """Response returned after processing a chat message."""

    reply: str
