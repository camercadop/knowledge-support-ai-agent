from collections.abc import Generator

from sqlalchemy import JSON, create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.types import Text

import app.infrastructure.database.sqlalchemy.postgresql.models  # noqa: F401 — registers all models with Base.metadata
from app.infrastructure.database.sqlalchemy.postgresql.base import Base

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
)

# JSONB is not supported by SQLite. Override the metadata column type so
# create_all succeeds for tables that are only used in SQLite-backed tests.
_chunks = Base.metadata.tables["document_chunks"]
_chunks.c["embedding"].type = Text()
_chunks.c["metadata"].type = JSON()


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection: object, connection_record: object) -> None:
    """Enable foreign key enforcement for every SQLite connection."""
    cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_tables() -> None:
    """Create all tables defined in Base.metadata against the in-memory engine."""
    Base.metadata.create_all(bind=engine)


SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session]:
    """Yield an in-memory SQLite session and ensure it is closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
