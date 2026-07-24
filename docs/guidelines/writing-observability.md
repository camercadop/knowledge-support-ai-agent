# Writing Observability

This document describes how to add OTel metrics and traces to a use case.

## Instruments

Domain-scoped instruments are grouped into frozen dataclasses and built by a factory function. See `app/infrastructure/observability/` for existing domains.

## Recording a metric

Use `timed_span` from `app/infrastructure/observability/utils` to wrap any operation that needs both a latency histogram and a trace span:

```python
from opentelemetry import trace

from app.infrastructure.observability.support.metrics import SupportMetrics
from app.infrastructure.observability.utils import timed_span

tracer = trace.get_tracer(__name__)


class AnswerQuestion:
    def __init__(self, metrics: SupportMetrics, ...) -> None:
        self._metrics = metrics
        self._tracer = tracer

    def handle(self, ...) -> ...:
        with timed_span("embed_query", self._metrics.embedding_duration, self._tracer):
            vector = self._embedding_model.embed(message)

        self._metrics.chunk_count.record(len(chunks))
```

For a plain counter (no span needed), call `.add()` directly:

```python
self._metrics.total_chunks_embedded.add(len(chunks))
```

## Adding a new domain

1. Create `app/infrastructure/observability/<domain>/metrics.py`.
2. Define a frozen dataclass holding the instruments and a `build_<domain>_metrics(meter)` factory.
3. Wire the metrics instance through the container and inject it into the use case constructor.

```python
from dataclasses import dataclass
from opentelemetry import metrics


@dataclass(frozen=True)
class MyDomainMetrics:
    """OTel instruments for the my-domain use case."""

    operation_duration: metrics.Histogram


def build_my_domain_metrics(meter: metrics.Meter) -> MyDomainMetrics:
    """Instantiate all my-domain instruments from the given meter."""
    return MyDomainMetrics(
        operation_duration=meter.create_histogram(
            "my_domain.operation_duration_seconds",
            unit="s",
            description="Time spent on the main operation",
        ),
    )
```

## Rules

- All instruments for a domain live in a single frozen dataclass in `app/infrastructure/observability/<domain>/metrics.py`.
- Instrument names follow the pattern `<domain>.<metric_name>_<unit>` (e.g. `rag.embedding_duration_seconds`).
- Use `timed_span` for any operation that needs both a latency histogram and a trace span.
- Metrics instances are injected into use cases — use cases must not import `build_*` factories directly.
- Never record PII (phone numbers, message content, user identifiers) as metric attributes.
