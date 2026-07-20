import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.application.support.answer_question import AnswerQuestion
from app.infrastructure.ai.chat.openai import OpenAIChatModel
from app.infrastructure.database.engine import get_db
from app.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()
logger = logging.getLogger(__name__)

_chat_model = OpenAIChatModel()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    """Receive a user message and return the assistant reply."""
    logger.info("Received chat request from %s", request.phone)
    use_case = AnswerQuestion(
        uow=SqlAlchemyUnitOfWork(db),
        chat_model=_chat_model,
    )
    reply = use_case.handle(request.phone, request.message)
    logger.info("Replied to %s", request.phone)
    return ChatResponse(reply=reply)
