from app.application.support.models.knowledge_base import KnowledgeBase
from app.application.support.ports.repositories.knowledge_base import (
    AbstractKnowledgeBaseRepository,
)
from app.infrastructure.database.sqlalchemy.postgresql.models.knowledge_base import (
    KnowledgeBase as KnowledgeBaseORM,
)
from app.infrastructure.database.sqlalchemy.postgresql.repositories.base import (
    SqlAlchemyRepository,
)


class KnowledgeBaseRepository(
    SqlAlchemyRepository[KnowledgeBaseORM, KnowledgeBase],
    AbstractKnowledgeBaseRepository,
):
    """Handles persistence operations for KnowledgeBase entities."""

    _orm_class = KnowledgeBaseORM

    def _to_domain(self, orm: KnowledgeBaseORM) -> KnowledgeBase:
        """Translate a KnowledgeBase ORM row into its domain model counterpart.

        Args:
            orm: The ORM row to translate.

        Returns:
            The corresponding KnowledgeBase domain instance.
        """
        return KnowledgeBase(id=orm.id, name=orm.name, description=orm.description)

    def create(self, name: str, description: str | None = None) -> KnowledgeBase:
        """Persist a new knowledge base and return it.

        Args:
            name: Human-readable name of the knowledge base.
            description: Optional description.

        Returns:
            The persisted KnowledgeBase.
        """
        return self._persist(name=name, description=description)
