from unittest.mock import MagicMock

from app.infrastructure.observability.utils import timed_span


def test_timed_span_opens_span_with_given_name() -> None:
    tracer = MagicMock()
    histogram = MagicMock()
    with timed_span("my_span", histogram, tracer):
        pass
    tracer.start_as_current_span.assert_called_once_with("my_span")


def test_timed_span_records_non_negative_duration() -> None:
    tracer = MagicMock()
    histogram = MagicMock()
    with timed_span("my_span", histogram, tracer):
        pass
    elapsed = histogram.record.call_args.args[0]
    assert elapsed >= 0


def test_timed_span_records_after_block_exits() -> None:
    tracer = MagicMock()
    histogram = MagicMock()
    with timed_span("my_span", histogram, tracer):
        assert not histogram.record.called
    assert histogram.record.called
