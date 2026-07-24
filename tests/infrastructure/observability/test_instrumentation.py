import pytest
from collections.abc import Generator
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry import metrics, trace

from app.infrastructure.observability.instrumentation import (
    InstrumentationConfig,
    OtelDefaultInstrumentation,
)


@pytest.fixture(autouse=True)
def otel_providers() -> Generator[InMemoryMetricReader, MeterProvider, TracerProvider]:
    """Create in-memory OTel providers for each test and return them.

    We avoid setting global providers here because tests run in a shared
    pytest session and overriding the global provider may be disallowed.
    Instead tests pass the created meter/tracer to the instrumentation
    instance directly.
    """
    reader = InMemoryMetricReader()
    meter_provider = MeterProvider(metric_readers=[reader])
    tracer_provider = TracerProvider()
    # Force-install providers into the opentelemetry modules so the
    # in-memory reader will receive exported metrics even if the SDK
    # previously installed a different global provider during the
    # pytest session.
    try:
        setattr(metrics, "_METER_PROVIDER", meter_provider)
    except Exception:
        pass
    try:
        setattr(trace, "_TRACER_PROVIDER", tracer_provider)
    except Exception:
        pass
    yield reader, meter_provider, tracer_provider


def _get_metric_names(reader: InMemoryMetricReader) -> set[str]:
    data = reader.get_metrics_data()
    if data is None:
        return set()
    return {
        metric.name
        for resource_metric in data.resource_metrics
        for scope_metric in resource_metric.scope_metrics
        for metric in scope_metric.metrics
    }


def _get_metric_points(reader: InMemoryMetricReader, name: str) -> list:
    data = reader.get_metrics_data()
    if data is None:
        return []
    for resource_metric in data.resource_metrics:
        for scope_metric in resource_metric.scope_metrics:
            for metric in scope_metric.metrics:
                if metric.name == name:
                    return list(metric.data.data_points)
    return []


# --- timed_spans ---


def test_timed_span_records_histogram(otel_providers) -> None:
    config = InstrumentationConfig(
        timed_spans={"my.op": ("my.duration", "s", "desc")},
    )
    reader, meter_provider, tracer_provider = otel_providers
    inst = OtelDefaultInstrumentation(
        config=config,
        meter=meter_provider.get_meter(__name__),
        tracer=tracer_provider.get_tracer(__name__),
    )
    with inst.span("my.op"):
        pass
    meter_provider.force_flush()
    metric_names = _get_metric_names(reader)
    assert "my.duration" in metric_names


def test_timed_span_records_positive_duration(otel_providers) -> None:
    config = InstrumentationConfig(
        timed_spans={"my.op": ("my.duration", "s", "desc")},
    )
    reader, meter_provider, tracer_provider = otel_providers
    inst = OtelDefaultInstrumentation(
        config=config,
        meter=meter_provider.get_meter(__name__),
        tracer=tracer_provider.get_tracer(__name__),
    )
    with inst.span("my.op"):
        pass
    meter_provider.force_flush()
    points = _get_metric_points(reader, "my.duration")
    assert len(points) == 1
    assert points[0].sum >= 0


def test_unknown_span_name_does_not_record_metric(otel_providers) -> None:
    config = InstrumentationConfig(
        timed_spans={"my.op": ("my.duration", "s", "desc")},
    )
    reader, meter_provider, tracer_provider = otel_providers
    inst = OtelDefaultInstrumentation(
        config=config,
        meter=meter_provider.get_meter(__name__),
        tracer=tracer_provider.get_tracer(__name__),
    )
    with inst.span("unknown.op"):
        pass
    meter_provider.force_flush()
    assert "my.duration" not in _get_metric_names(reader)


# --- record_metrics ---


def test_record_metrics_histogram(otel_providers) -> None:
    config = InstrumentationConfig(
        metrics={"chunk_count": ("histogram", "rag.chunk_count", None, "desc")},
    )
    reader, meter_provider, tracer_provider = otel_providers
    inst = OtelDefaultInstrumentation(
        config=config,
        meter=meter_provider.get_meter(__name__),
        tracer=tracer_provider.get_tracer(__name__),
    )
    inst.record_metrics({"chunk_count": 3})
    meter_provider.force_flush()
    points = _get_metric_points(reader, "rag.chunk_count")
    assert len(points) == 1
    assert points[0].sum == 3


def test_record_metrics_counter(otel_providers) -> None:
    config = InstrumentationConfig(
        metrics={"total": ("counter", "ingest.total_chunks_embedded", None, "desc")},
    )
    reader, meter_provider, tracer_provider = otel_providers
    inst = OtelDefaultInstrumentation(
        config=config,
        meter=meter_provider.get_meter(__name__),
        tracer=tracer_provider.get_tracer(__name__),
    )
    inst.record_metrics({"total": 5})
    meter_provider.force_flush()
    points = _get_metric_points(reader, "ingest.total_chunks_embedded")
    assert len(points) == 1
    assert points[0].value == 5


def test_record_metrics_skips_none_values(otel_providers) -> None:
    config = InstrumentationConfig(
        metrics={"chunk_count": ("histogram", "rag.chunk_count", None, "desc")},
    )
    reader, meter_provider, tracer_provider = otel_providers
    inst = OtelDefaultInstrumentation(
        config=config,
        meter=meter_provider.get_meter(__name__),
        tracer=tracer_provider.get_tracer(__name__),
    )
    inst.record_metrics({"chunk_count": None})
    meter_provider.force_flush()
    assert "rag.chunk_count" not in _get_metric_names(reader)


def test_record_metrics_ignores_unknown_keys(otel_providers) -> None:
    config = InstrumentationConfig()
    reader, meter_provider, tracer_provider = otel_providers
    inst = OtelDefaultInstrumentation(
        config=config,
        meter=meter_provider.get_meter(__name__),
        tracer=tracer_provider.get_tracer(__name__),
    )
    inst.record_metrics({"unknown": 99})  # must not raise
