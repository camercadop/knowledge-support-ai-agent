# observability

OTel instrumentation for the application. Contains the base instrumentation class, per-use-case configuration constants, and a null adapter.

## Modules

- `instrumentation.py` — core instrumentation types: `InstrumentationConfig`, `NullInstrumentation`, and `OtelDefaultInstrumentation`
- `utils.py` — shared helpers

## Sub-packages

- `definitions/` — `InstrumentationConfig` constants grouped by domain

## Instrumentation pattern

Each use case has a module-level `InstrumentationConfig` constant that declares its spans and metrics. `OtelDefaultInstrumentation` is instantiated with that config via `BaseContainer._instrumentation`, which caches the instance by config.

`InstrumentationConfig` accepts two optional fields:

- `timed_spans` — maps a span name to `(metric_name, unit, description)`. The instrumentation wraps the span and records its duration to a histogram on exit.
- `metrics` — maps a metric key to `(kind, metric_name, unit, description)`. `kind` is `"histogram"` or `"counter"`.

```python
ANSWER_QUESTION_INSTRUMENTATION = InstrumentationConfig(
    timed_spans={
        "embedding.embed": ("rag.embedding_duration_seconds", "s", "..."),
    },
    metrics={
        "rag.chunk_count": ("histogram", "rag.chunk_count", None, "..."),
    },
)
```

Use cases with no metrics or spans pass an empty `InstrumentationConfig()`, which produces a no-op beyond basic tracing.
