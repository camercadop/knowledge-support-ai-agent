# mypy: ignore-errors

from app.config.settings import settings


def setup_telemetry() -> None:
    """Initialize OpenTelemetry SDK with OTLP HTTP exporters.

    Sets up a TracerProvider and MeterProvider backed by OTLP HTTP exporters
    pointing at the configured endpoint. Does nothing when OTEL_ENABLED is false,
    leaving the no-op global providers in place.
    """
    if not settings.otel_enabled:
        return

    from opentelemetry import metrics, trace
    from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
        OTLPMetricExporter,
    )
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    resource = Resource.create({"service.name": settings.otel_service_name})

    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(endpoint=f"{settings.otel_endpoint}/v1/traces")
        )
    )
    trace.set_tracer_provider(tracer_provider)

    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[
            PeriodicExportingMetricReader(
                OTLPMetricExporter(endpoint=f"{settings.otel_endpoint}/v1/metrics")
            )
        ],
    )
    metrics.set_meter_provider(meter_provider)
