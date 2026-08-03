import pytest
from sqlalchemy.orm import Session

from app.application.support.use_cases.knowledge_base import KnowledgeBaseCRUD
from app.infrastructure.database.sqlalchemy.postgresql.unit_of_work.knowledge import (
    SqlAlchemyKnowledgeUnitOfWork,
)


@pytest.fixture()
def uow(pg_db: Session) -> SqlAlchemyKnowledgeUnitOfWork:
    """Return a KnowledgeUnitOfWork backed by the PostgreSQL session."""
    return SqlAlchemyKnowledgeUnitOfWork(pg_db)


@pytest.fixture()
def use_case(uow: SqlAlchemyKnowledgeUnitOfWork) -> KnowledgeBaseCRUD:
    """Return a KnowledgeBaseCRUD bound to the test session."""
    return KnowledgeBaseCRUD(uow=uow)


# --- create ---


def test_create_returns_knowledge_base_with_correct_name(
    use_case: KnowledgeBaseCRUD,
) -> None:
    kb = use_case.create(name="Support", description="Support KB")
    assert kb.name == "Support"
    assert kb.description == "Support KB"


def test_create_assigns_id(use_case: KnowledgeBaseCRUD) -> None:
    kb = use_case.create(name="Support")
    assert kb.id is not None


def test_create_without_description(use_case: KnowledgeBaseCRUD) -> None:
    kb = use_case.create(name="Support")
    assert kb.description is None


# --- list ---


def test_list_returns_created_knowledge_bases(use_case: KnowledgeBaseCRUD) -> None:
    use_case.create(name="KB One")
    use_case.create(name="KB Two")
    results = use_case.list()
    names = [kb.name for kb in results]
    assert "KB One" in names
    assert "KB Two" in names


def test_list_returns_empty_when_none_exist(use_case: KnowledgeBaseCRUD) -> None:
    assert use_case.list() == []


# --- get_by_id ---


def test_get_by_id_returns_correct_knowledge_base(
    use_case: KnowledgeBaseCRUD,
) -> None:
    kb = use_case.create(name="Support")
    result = use_case.get_by_id(kb.id)
    assert result is not None
    assert result.id == kb.id


def test_get_by_id_returns_none_for_missing_id(use_case: KnowledgeBaseCRUD) -> None:
    import uuid

    assert use_case.get_by_id(uuid.uuid4()) is None


# --- update ---


def test_update_changes_name(use_case: KnowledgeBaseCRUD) -> None:
    kb = use_case.create(name="Old Name")
    updated = use_case.update(kb, name="New Name")
    assert updated is not None
    assert updated.name == "New Name"


def test_update_changes_description(use_case: KnowledgeBaseCRUD) -> None:
    kb = use_case.create(name="Support", description="Old")
    updated = use_case.update(kb, description="New")
    assert updated is not None
    assert updated.description == "New"


def test_update_persists_changes(use_case: KnowledgeBaseCRUD) -> None:
    kb = use_case.create(name="Old Name")
    use_case.update(kb, name="New Name")
    persisted = use_case.get_by_id(kb.id)
    assert persisted is not None
    assert persisted.name == "New Name"


# --- delete ---


def test_delete_removes_knowledge_base(use_case: KnowledgeBaseCRUD) -> None:
    kb = use_case.create(name="To Delete")
    use_case.delete(kb.id)
    assert use_case.get_by_id(kb.id) is None


def test_delete_nonexistent_does_not_raise(use_case: KnowledgeBaseCRUD) -> None:
    import uuid

    use_case.delete(uuid.uuid4())
