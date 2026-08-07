import uuid

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.application.shared.use_cases.crud import CRUDUseCase
from app.application.support.models.knowledge_base import KnowledgeBase
from app.application.support.ports.repositories.knowledge_base_config import (
    AbstractKnowledgeBaseConfigRepository,
)
from app.container.support import SupportContainer
from app.infrastructure.database.sqlalchemy.postgresql.engine import get_db
from app.infrastructure.database.sqlalchemy.postgresql.unit_of_work.base import (
    SqlAlchemyUnitOfWork,
)
from app.infrastructure.routers.crud import CRUDRouter
from app.schemas.knowledge_base import (
    KnowledgeBaseConfigEntryRequest,
    KnowledgeBaseConfigResponse,
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


def _get_config_repo(
    db: Session = Depends(get_db),
) -> AbstractKnowledgeBaseConfigRepository:
    """Resolve the config repository from the current session."""
    return SqlAlchemyUnitOfWork(db).get(AbstractKnowledgeBaseConfigRepository)


router = CRUDRouter(
    prefix="/knowledge-bases",
    response_model=KnowledgeBaseResponse,
    get_use_case=_get_use_case,
    to_response=_to_response,
    create_schema=KnowledgeBaseCreateRequest,
    update_schema=KnowledgeBaseUpdateRequest,
)


@router.get(
    "/knowledge-bases/{knowledge_base_id}/config",
    response_model=KnowledgeBaseConfigResponse,
)
def get_config(
    knowledge_base_id: uuid.UUID,
    repo: AbstractKnowledgeBaseConfigRepository = Depends(_get_config_repo),
) -> KnowledgeBaseConfigResponse:
    """Return all configuration entries for the given knowledge base."""
    return KnowledgeBaseConfigResponse(
        config=repo.get_by_knowledge_base_id(knowledge_base_id)
    )


@router.put(
    "/knowledge-bases/{knowledge_base_id}/config",
    response_model=KnowledgeBaseConfigResponse,
)
def upsert_config(
    knowledge_base_id: uuid.UUID,
    body: KnowledgeBaseConfigEntryRequest,
    repo: AbstractKnowledgeBaseConfigRepository = Depends(_get_config_repo),
) -> KnowledgeBaseConfigResponse:
    """Upsert a single configuration entry for the given knowledge base."""
    repo.set(knowledge_base_id, body.key, body.value)
    return KnowledgeBaseConfigResponse(
        config=repo.get_by_knowledge_base_id(knowledge_base_id)
    )


@router.delete(
    "/knowledge-bases/{knowledge_base_id}/config/{key}",
    status_code=204,
)
def delete_config(
    knowledge_base_id: uuid.UUID,
    key: str,
    repo: AbstractKnowledgeBaseConfigRepository = Depends(_get_config_repo),
) -> None:
    """Remove a single configuration entry from the given knowledge base.

    Raises:
        HTTPException: 404 if the key does not exist.
    """
    config = repo.get_by_knowledge_base_id(knowledge_base_id)
    if key not in config:
        raise HTTPException(status_code=404, detail="Config key not found")
    repo.delete(knowledge_base_id, key)
