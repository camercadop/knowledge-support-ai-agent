import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.container.support import SupportContainer
from app.infrastructure.database.sqlalchemy.postgresql.engine import get_db
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()
logger = logging.getLogger(__name__)


def get_container(request: Request) -> SupportContainer:
    """Return the support container from request state.

    Args:
        request: The current FastAPI request.

    Returns:
        The SupportContainer instance stored on app.state.container.support.
    """
    container: SupportContainer = request.app.state.container.support
    return container


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    container: SupportContainer = Depends(get_container),
    db: Session = Depends(get_db),
) -> ChatResponse:
    """Receive a user message and return the assistant reply."""
    logger.info("Received chat request from %s", request.phone)
    reply = container.answer_question(db).handle(request.phone, request.message)
    logger.info("Replied to %s", request.phone)
    return ChatResponse(reply=reply)
