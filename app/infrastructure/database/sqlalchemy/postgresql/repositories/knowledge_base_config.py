import uuid

from sqlalchemy.orm import Session

from app.application.support.models.knowledge_base_config import (
    KnowledgeBaseConfig as KnowledgeBaseConfigDomain,
)
from app.application.support.ports.repositories.knowledge_base_config import (
    AbstractKnowledgeBaseConfigRepository,
)
from app.infrastructure.database.sqlalchemy.postgresql.models.knowledge_base_config import (  # noqa: E501
    KnowledgeBaseConfig as KnowledgeBaseConfigORM,
)
from app.infrastructure.database.sqlalchemy.postgresql.repositories.registry import (
    repository,
)


@repository(AbstractKnowledgeBaseConfigRepository)
class KnowledgeBaseConfigRepository(AbstractKnowledgeBaseConfigRepository):
    """Handles persistence operations for KnowledgeBaseConfig entries."""

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self._db = db

    def _to_domain(self, orm: KnowledgeBaseConfigORM) -> KnowledgeBaseConfigDomain:
        """Translate a KnowledgeBaseConfig ORM row into its domain model counterpart.

        Args:
            orm: The ORM row to translate.

        Returns:
            The corresponding KnowledgeBaseConfig domain instance.
        """
        return KnowledgeBaseConfigDomain(
            id=orm.id,
            knowledge_base_id=orm.knowledge_base_id,
            key=orm.key,
            value=orm.value,
        )

    def set(
        self, knowledge_base_id: uuid.UUID, key: str, value: str
    ) -> KnowledgeBaseConfigDomain:
        """Upsert a configuration entry for the given knowledge base.

        Loads the existing row if present and updates its value; otherwise
        creates a new row. Flushes the session so the change is visible within
        the current transaction.

        Args:
            knowledge_base_id: The knowledge base this entry belongs to.
            key: The configuration key.
            value: The configuration value, always stored as a string.

        Returns:
            The persisted KnowledgeBaseConfig domain instance.
        """
        orm = (
            self._db.query(KnowledgeBaseConfigORM)
            .filter_by(knowledge_base_id=knowledge_base_id, key=key)
            .one_or_none()
        )
        if orm is None:
            orm = KnowledgeBaseConfigORM(
                id=uuid.uuid4(),
                knowledge_base_id=knowledge_base_id,
                key=key,
                value=value,
            )
            self._db.add(orm)
        else:
            orm.value = value
        self._db.flush()
        return self._to_domain(orm)

    def get_by_knowledge_base_id(self, knowledge_base_id: uuid.UUID) -> dict[str, str]:
        """Return all configuration entries for the given knowledge base as a dict.

        Args:
            knowledge_base_id: The knowledge base to load config for.

        Returns:
            A dict mapping each key to its value. Empty dict if no entries exist.
        """
        rows = (
            self._db.query(KnowledgeBaseConfigORM)
            .filter_by(knowledge_base_id=knowledge_base_id)
            .all()
        )
        return {row.key: row.value for row in rows}

    def delete(self, knowledge_base_id: uuid.UUID, key: str) -> None:
        """Remove a single configuration entry.

        Does nothing if the entry does not exist.

        Args:
            knowledge_base_id: The knowledge base the entry belongs to.
            key: The configuration key to remove.
        """
        orm = (
            self._db.query(KnowledgeBaseConfigORM)
            .filter_by(knowledge_base_id=knowledge_base_id, key=key)
            .one_or_none()
        )
        if orm is not None:
            self._db.delete(orm)
            self._db.flush()
