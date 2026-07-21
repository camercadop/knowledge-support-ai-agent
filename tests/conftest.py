from collections.abc import Generator

import pytest
from sqlalchemy.orm import Session

from app.infrastructure.database.sqlalchemy.postgresql.base import Base
from app.infrastructure.database.sqlalchemy.sqlite.engine import (
    SessionLocal,
    create_tables,
    engine,
)


@pytest.fixture()
def db() -> Generator[Session]:
    """Yield an in-memory SQLite session with a clean schema for each test."""
    Base.metadata.drop_all(bind=engine)
    create_tables()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
