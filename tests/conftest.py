import os
from collections.abc import Generator

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.database.sqlalchemy.postgresql.base import Base
from app.infrastructure.database.sqlalchemy.sqlite.engine import (
    SessionLocal,
    create_tables,
    engine,
)

_TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/knowledge_agent",
)


@pytest.fixture(scope="session")
def pg_engine() -> Generator[Engine]:
    """Yield a SQLAlchemy engine connected to the running PostgreSQL container.

    Requires the container to be running (docker compose up -d).
    Override the connection string via the TEST_DATABASE_URL environment variable.
    """
    eng = create_engine(_TEST_DATABASE_URL)
    with eng.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(bind=eng)
    yield eng
    Base.metadata.drop_all(bind=eng)
    eng.dispose()


@pytest.fixture()
def pg_db(pg_engine: Engine) -> Generator[Session]:
    """Yield a PostgreSQL session that rolls back after each test.

    Uses a savepoint so that use cases calling commit() do not permanently
    write data — the outer transaction is always rolled back on teardown.
    """
    connection = pg_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    session.begin_nested()  # savepoint — absorbs inner commits
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


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
