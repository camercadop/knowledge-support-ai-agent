from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest

from app.application.shared.security.logger import log_security_event


@pytest.fixture()
def mock_security_logger() -> Generator[MagicMock]:
    with patch(
        "app.application.shared.security.logger.security_logger",
    ) as logger:
        yield logger


def test_log_security_event_calls_warning_by_default(
    mock_security_logger: MagicMock,
) -> None:
    log_security_event("http.rate_limit_exceeded")
    mock_security_logger.warning.assert_called_once()


def test_log_security_event_calls_info_when_level_is_info(
    mock_security_logger: MagicMock,
) -> None:
    log_security_event("support.message_rejected", level="info")
    mock_security_logger.info.assert_called_once()


def test_log_security_event_calls_error_when_level_is_error(
    mock_security_logger: MagicMock,
) -> None:
    log_security_event("http.invalid_token", level="error")
    mock_security_logger.error.assert_called_once()


def test_log_security_event_passes_event_in_message(
    mock_security_logger: MagicMock,
) -> None:
    log_security_event("http.rate_limit_exceeded")
    call_args = mock_security_logger.warning.call_args
    assert call_args[0][0] == "security event: %s"
    assert call_args[0][1] == "http.rate_limit_exceeded"


def test_log_security_event_includes_security_event_in_extra(
    mock_security_logger: MagicMock,
) -> None:
    log_security_event("http.rate_limit_exceeded")
    call_kwargs = mock_security_logger.warning.call_args.kwargs
    extra = call_kwargs["extra"]
    assert extra["security_event"] == "http.rate_limit_exceeded"


def test_log_security_event_includes_extra_fields(
    mock_security_logger: MagicMock,
) -> None:
    log_security_event(
        "support.message_rejected",
        user_id="abc-123",
        reason="blocked",
    )
    call_kwargs = mock_security_logger.warning.call_args.kwargs
    extra = call_kwargs["extra"]
    assert extra["security_event"] == "support.message_rejected"
    assert extra["user_id"] == "abc-123"
    assert extra["reason"] == "blocked"


def test_log_security_event_raises_value_error_for_invalid_level(
    mock_security_logger: MagicMock,
) -> None:
    with pytest.raises(ValueError):
        log_security_event("http.rate_limit_exceeded", level="critical")
