from sqlalchemy.orm import Session

from app.application.shared.ports.unit_of_work import UnitOfWork


class SqlAlchemyUnitOfWork(UnitOfWork):
    """Base SQLAlchemy unit of work that provides session management and commit.

    All domain-specific SQLAlchemy UoW classes must inherit from this base.
    Subclasses should initialize their repositories in __init__ using self._db,
    and must not override commit() unless they need custom transaction behaviour.
    """

    def __init__(self, db: Session) -> None:
        """Initialize with an active database session."""
        self._db = db

    def commit(self) -> None:
        """Commit the current session transaction."""
        self._db.commit()
