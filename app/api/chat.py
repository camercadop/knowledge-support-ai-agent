from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.application.chat.service import ChatService
from app.infrastructure.database.engine import get_db
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    """Receive a user message and return the assistant reply."""
    reply = ChatService(db).handle(request.phone, request.message)
    return ChatResponse(reply=reply)
