# mypy: ignore-errors
import time
from collections.abc import Generator
from contextlib import contextmanager

from opentelemetry import metrics, trace


@contextmanager
def timed_span(
    name: str, histogram: metrics.Histogram, tracer: trace.Tracer
) -> Generator[None]:
    """Context manager that wraps a block in an OTel span and records its duration.

    Opens a child span with the given name, measures wall-clock elapsed time, and
    records it to the provided histogram on exit. Use this for any operation that
    needs both tracing and a latency metric.

    Args:
        name: Span name passed to the tracer.
        histogram: OTel histogram to record the elapsed duration in seconds.
        tracer: Tracer used to open the child span.

    Example:
        with timed_span("embed_query", latency_histogram, tracer):
            result = embedding_client.embed(text)
    """
    with tracer.start_as_current_span(name):
        t0 = time.perf_counter()
        yield
        histogram.record(time.perf_counter() - t0)
