import uuid
from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.application.shared.use_cases.crud import CRUDUseCase
from app.infrastructure.database.sqlalchemy.postgresql.engine import get_db


def CRUDRouter[M, CreateSchema: BaseModel, UpdateSchema: BaseModel](
    prefix: str,
    response_model: type[Any],
    get_use_case: Callable[[Request, Session], CRUDUseCase[M]],
    to_response: Callable[[M], Any],
    create_schema: type[CreateSchema],
    update_schema: type[UpdateSchema],
) -> APIRouter:
    """Build an APIRouter with create, list, get_by_id, update, and delete endpoints.

    Args:
        prefix: URL prefix for all routes (e.g. '/knowledge-bases').
        response_model: Pydantic response schema used for serialization.
        get_use_case: Callable that receives the request and db session and
            returns a bound CRUDUseCase instance.
        to_response: Callable that maps a domain model instance to a response schema.
        create_schema: Pydantic schema for POST request bodies. Field names must
            match the use case's create() parameter names.
        update_schema: Pydantic schema for PATCH request bodies.

    Returns:
        A fully wired APIRouter with CRUD endpoints.
    """
    router = APIRouter()

    def _use_case(request: Request, db: Session = Depends(get_db)) -> CRUDUseCase[M]:
        return get_use_case(request, db)

    def _make_create(schema: type[Any]) -> Any:
        def create_entity(
            body: Any,
            use_case: CRUDUseCase[M] = Depends(_use_case),
        ) -> Any:
            """Create a new entity."""
            return to_response(use_case.create(**body.model_dump()))

        create_entity.__annotations__["body"] = schema
        return create_entity

    def _make_update(schema: type[Any]) -> Any:
        def update_entity(
            entity_id: uuid.UUID,
            body: Any,
            use_case: CRUDUseCase[M] = Depends(_use_case),
        ) -> Any:
            """Partially update the entity with the given id."""
            entity = use_case.get_by_id(entity_id)
            if entity is None:
                raise HTTPException(status_code=404, detail="Not found")
            updated = use_case.update(entity, **body.model_dump(exclude_unset=True))
            return to_response(updated)

        update_entity.__annotations__["body"] = schema
        return update_entity

    router.add_api_route(
        prefix,
        _make_create(create_schema),
        methods=["POST"],
        response_model=response_model,
        status_code=201,
    )

    @router.get(prefix, response_model=list[response_model])  # type: ignore[valid-type]
    def list_entities(use_case: CRUDUseCase[M] = Depends(_use_case)) -> list[Any]:
        """Return all entities."""
        return [to_response(e) for e in use_case.list()]

    @router.get(f"{prefix}/{{entity_id}}", response_model=response_model)
    def get_entity(
        entity_id: uuid.UUID, use_case: CRUDUseCase[M] = Depends(_use_case)
    ) -> Any:
        """Return the entity with the given id."""
        entity = use_case.get_by_id(entity_id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Not found")
        return to_response(entity)

    router.add_api_route(
        f"{prefix}/{{entity_id}}",
        _make_update(update_schema),
        methods=["PATCH"],
        response_model=response_model,
    )

    @router.delete(f"{prefix}/{{entity_id}}", status_code=204)
    def delete_entity(
        entity_id: uuid.UUID, use_case: CRUDUseCase[M] = Depends(_use_case)
    ) -> None:
        """Delete the entity with the given id."""
        entity = use_case.get_by_id(entity_id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Not found")
        use_case.delete(entity_id)

    return router
