# Writing Observability

This document describes how to add OTel metrics and traces to a use case.

## How it works

Each use case has a module-level `InstrumentationConfig` constant that declares its spans and metrics. `OtelDefaultInstrumentation` is the single concrete class — it accepts an `InstrumentationConfig` on construction and creates the corresponding OTel instruments via `_build_instruments`. Instances are cached and injected via `BaseContainer._instrumentation`.

## Using instrumentation in a use case

Inject `instrumentation: BaseInstrumentation` in the use case constructor and use it to wrap operations in spans and record metrics.

```python
class MyUseCase:
    def __init__(self, ..., instrumentation: BaseInstrumentation) -> None:
        ...
        self._instrumentation = instrumentation

    def handle(self, ...) -> ...:
        with self._instrumentation.root_span("my_use_case.handle"):
            with self._instrumentation.span("operation.run"):
                result = self._do_work()
            self._instrumentation.record_metrics({"my_domain.item_count": len(result)})
            return result
```

- `root_span` — wraps the entire use case execution in a top-level trace span. Call it once at the top of `handle`.
- `span` — wraps a named sub-operation and records its duration if a matching `timed_spans` entry exists.
- `record_metrics` — records arbitrary key-value pairs to their registered instruments. Keys not declared in `metrics` are silently ignored.

## Adding instrumentation to a new use case

1. Add an `InstrumentationConfig` constant to `app/infrastructure/observability/definitions/<domain>.py`.
2. Wire it in the domain container via `self._instrumentation(<CONSTANT>)` and inject it into the use case constructor as `instrumentation: BaseInstrumentation`.

```python
# app/infrastructure/observability/definitions/support.py
MY_USE_CASE_INSTRUMENTATION = InstrumentationConfig(
    timed_spans={
        "operation.run": ("my_domain.operation_duration_seconds", "s", "Time spent on the main operation"),
    },
    metrics={
        "my_domain.item_count": ("histogram", "my_domain.item_count", None, "Number of items processed"),
        "my_domain.total_processed": ("counter", "my_domain.total_processed", None, "Cumulative items processed"),
    },
)
```

## Config conventions

### `timed_spans`

Maps a span name (passed to `instrumentation.span(name)`) to a `(metric_name, unit, description)` tuple.

The instrumentation wraps the block in an OTel span and records its wall-clock duration to a histogram on exit. `unit` may be `None`.

```python
timed_spans={
    "embedding.embed": ("rag.embedding_duration_seconds", "s", "Time spent generating the query embedding"),
}
```

### `metrics`

Maps a metric key (passed to `instrumentation.record_metrics({key: value})`) to a `(kind, metric_name, unit, description)` tuple.

`kind` must be `"histogram"` or `"counter"`. `unit` may be `None`.

```python
metrics={
    "rag.chunk_count": ("histogram", "rag.chunk_count", None, "Number of chunks included in RAG context per turn"),
    "ingest.total_chunks_embedded": ("counter", "ingest.total_chunks_embedded", None, "Cumulative count of chunks embedded"),
}
```

## Use cases with no metrics

Pass an empty `InstrumentationConfig()` for use cases that only need span tracing and no metrics. Both fields default to empty dicts, so `record_metrics` is a safe no-op.

## Rules

- Instrument names follow the pattern `<domain>.<metric_name>_<unit>` (e.g. `rag.embedding_duration_seconds`).
- One `InstrumentationConfig` constant per use case — do not share configs across use cases.
- Instrumentation instances are injected into use cases — use cases must not instantiate them directly.
- Never record PII (phone numbers, message content, user identifiers) as metric attributes.
