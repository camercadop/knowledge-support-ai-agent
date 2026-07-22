from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy.orm import Session

from app.container import ApplicationContainer
from app.infrastructure.database.sqlalchemy.postgresql.engine import SessionLocal


@contextmanager
def request_context() -> Generator[tuple[ApplicationContainer, Session]]:
    """Provide a container and database session for a CLI command.

    Instantiates the ApplicationContainer and opens a database session,
    yielding both to the caller. Guarantees the session is closed on exit.

    Yields:
        A tuple of (ApplicationContainer, Session).
    """
    container = ApplicationContainer()
    db = SessionLocal()
    try:
        yield container, db
    finally:
        db.close()
