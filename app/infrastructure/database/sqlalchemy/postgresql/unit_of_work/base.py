from sqlalchemy.orm import Session

from app.application.shared.ports.unit_of_work import UnitOfWork


class SqlAlchemyUnitOfWork(UnitOfWork):
    """Base SQLAlchemy unit of work that provides session management and commit.

    All domain-specific SQLAlchemy UoW classes must inherit from this base.
    Repositories are resolved lazily via ``get(port)`` using the global repository
    registry and cached for the lifetime of the unit of work instance.
    """

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self._db = db
        self._cache: dict[type, object] = {}

    def commit(self) -> None:
        """Commit the current session transaction."""
        self._db.commit()

    def get[R](self, repo_type: type[R]) -> R:
        """Return the repository instance for the given port type.

        Looks up the concrete class from the global repository registry,
        instantiates it with the current session on first access, and caches
        it for the lifetime of this unit of work.

        The repositories package is imported lazily on first call to avoid
        circular imports at module load time.

        Args:
            repo_type: The abstract repository port class to resolve.

        Returns:
            The concrete repository instance bound to the current session.

        Raises:
            KeyError: If no repository is registered for the given port.
        """
        if repo_type not in self._cache:
            import app.infrastructure.database.sqlalchemy.postgresql.repositories  # noqa: F401
            from app.infrastructure.database.sqlalchemy.postgresql.repositories.registry import (
                get_repository,
            )

            self._cache[repo_type] = get_repository(repo_type)(self._db)
        return self._cache[repo_type]  # type: ignore[return-value]
