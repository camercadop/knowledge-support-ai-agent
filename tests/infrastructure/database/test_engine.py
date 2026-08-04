from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from app.infrastructure.database.sqlalchemy.postgresql.engine import get_db


def test_get_db_yields_session() -> None:
    """get_db yields a Session instance."""
    with patch("app.infrastructure.database.sqlalchemy.postgresql.engine.SessionLocal") as mock_session_local:
        mock_session = MagicMock(spec=Session)
        mock_session_local.return_value = mock_session
        gen = get_db()
        db = next(gen)
        assert db is mock_session
        gen.close()


def test_get_db_closes_session_after_yield() -> None:
    """get_db closes the session after the generator is exhausted."""
    with patch("app.infrastructure.database.sqlalchemy.postgresql.engine.SessionLocal") as mock_session_local:
        mock_session = MagicMock(spec=Session)
        mock_session_local.return_value = mock_session
        gen = get_db()
        next(gen)
        gen.close()
        mock_session.close.assert_called_once()


def test_get_db_closes_session_on_exception() -> None:
    """get_db closes the session even when an exception occurs in the caller."""
    with patch("app.infrastructure.database.sqlalchemy.postgresql.engine.SessionLocal") as mock_session_local:
        mock_session = MagicMock(spec=Session)
        mock_session_local.return_value = mock_session
        gen = get_db()
        next(gen)
        with pytest.raises(RuntimeError):
            gen.throw(RuntimeError("test error"))
        mock_session.close.assert_called_once()
