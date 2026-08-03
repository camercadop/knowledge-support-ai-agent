from fastapi import Request
from sqlalchemy.orm import Session

from app.application.shared.use_cases.crud import CRUDUseCase
from app.application.support.models.knowledge_base import KnowledgeBase
from app.container.support import SupportContainer
from app.infrastructure.routers.crud import CRUDRouter
from app.schemas.knowledge_base import (
    KnowledgeBaseCreateRequest,
    KnowledgeBaseResponse,
    KnowledgeBaseUpdateRequest,
)


def get_container(request: Request) -> SupportContainer:
    """Return the support container from request state.

    Args:
        request: The current FastAPI request.

    Returns:
        The SupportContainer instance stored on app.state at startup.
    """
    container: SupportContainer = request.app.state.container.support
    return container


def _to_response(kb: KnowledgeBase) -> KnowledgeBaseResponse:
    return KnowledgeBaseResponse(id=kb.id, name=kb.name, description=kb.description)


def _get_use_case(request: Request, db: Session) -> CRUDUseCase[KnowledgeBase]:
    return get_container(request).knowledge_base_crud(db)


router = CRUDRouter(
    prefix="/knowledge-bases",
    response_model=KnowledgeBaseResponse,
    get_use_case=_get_use_case,
    to_response=_to_response,
    create_schema=KnowledgeBaseCreateRequest,
    update_schema=KnowledgeBaseUpdateRequest,
)
