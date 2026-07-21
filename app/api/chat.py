import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.application.support.answer_question import AnswerQuestion
from app.infrastructure.ai.chat.openai import OpenAIChatModel
from app.infrastructure.ai.embeddings.openai import OpenAIEmbeddingModel
from app.infrastructure.database.sqlalchemy.engine import get_db
from app.infrastructure.database.sqlalchemy.unit_of_work.messaging import (
    SqlAlchemyMessagingUnitOfWork,
)
from app.infrastructure.vectorstores.pgvector.store import PgVectorStore
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()
logger = logging.getLogger(__name__)

_chat_model = OpenAIChatModel()
_embedding_model = OpenAIEmbeddingModel()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    """Receive a user message and return the assistant reply."""
    safe_phone = request.phone.replace("\n", " ").replace("\r", " ")
    logger.info("Received chat request from %s", safe_phone)
    use_case = AnswerQuestion(
        uow=SqlAlchemyMessagingUnitOfWork(db),
        chat_model=_chat_model,
        embedding_model=_embedding_model,
        vector_store=PgVectorStore(db),
    )
    reply = use_case.handle(request.phone, request.message)
    logger.info("Replied to %s", safe_phone)
    return ChatResponse(reply=reply)
