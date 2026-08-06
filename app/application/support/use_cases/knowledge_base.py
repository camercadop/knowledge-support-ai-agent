from app.application.shared.ports.unit_of_work import UnitOfWork
from app.application.shared.use_cases.crud import CRUDUseCase
from app.application.support.models.knowledge_base import KnowledgeBase
from app.application.support.ports.repositories.knowledge_base import (
    AbstractKnowledgeBaseRepository,
)


class KnowledgeBaseCRUD(CRUDUseCase[KnowledgeBase]):
    """CRUD use case for knowledge bases."""

    def __init__(self, uow: UnitOfWork) -> None:
        """Initialize with a knowledge-scoped unit of work.

        Args:
            uow: The unit of work exposing the knowledge base repository.
        """
        super().__init__(uow)
        self._repository: AbstractKnowledgeBaseRepository = self._get_repository()

    def _get_repository(self) -> AbstractKnowledgeBaseRepository:
        """Return the knowledge base repository bound to the current transaction."""
        return self._uow.get(AbstractKnowledgeBaseRepository)

    def create(self, name: str, description: str | None = None) -> KnowledgeBase:
        """Create a new knowledge base.

        Args:
            name: Human-readable name of the knowledge base.
            description: Optional description.

        Returns:
            The persisted KnowledgeBase.
        """
        knowledge_base = self._repository.create(name=name, description=description)
        self._commit()

        return knowledge_base
