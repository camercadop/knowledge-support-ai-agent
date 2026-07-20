from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Payload for sending a chat message."""

    phone: str
    message: str


class ChatResponse(BaseModel):
    """Response returned after processing a chat message."""

    reply: str
