import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.application.support.answer_question import AnswerQuestion
from app.infrastructure.database.engine import get_db
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    """Receive a user message and return the assistant reply."""
    logger.info("Received chat request from %s", request.phone)
    reply = AnswerQuestion(db).handle(request.phone, request.message)
    logger.info("Replied to %s", request.phone)
    return ChatResponse(reply=reply)
