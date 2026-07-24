# mypy: ignore-errors
import time
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any

from opentelemetry import metrics, trace

from app.application.ports.observability import BaseInstrumentation


@dataclass(frozen=True)
class InstrumentationConfig:
    """Configuration for OtelDefaultInstrumentation.

    timed_spans maps a span name to a tuple of (metric_name, unit, description).
    Each entry produces a histogram whose duration is recorded when the span exits.

    metrics maps a metric key to a tuple of (kind, metric_name, unit, description).
    kind must be "histogram" or "counter". unit may be None.
    """

    timed_spans: dict[str, tuple[str, str | None, str]] = field(default_factory=dict)
    metrics: dict[str, tuple[str, str, str | None, str]] = field(default_factory=dict)


class NullInstrumentation(BaseInstrumentation):
    """No-op instrumentation used as the default when no backend is configured.

    All methods are safe no-ops. Use this as the default value for instrumentation
    parameters in use cases to avoid None checks.
    """

    @contextmanager
    def root_span(self, name: str) -> Generator[None]:
        """No-op root span."""
        yield

    @contextmanager
    def span(self, name: str) -> Generator[None]:
        """No-op span."""
        yield

    def record_metrics(self, data: dict[str, Any]) -> None:
        """No-op metrics recording."""


class OtelDefaultInstrumentation(BaseInstrumentation):
    """OTel instrumentation with span tracing and metric recording.

    Accepts an InstrumentationConfig that declares timed spans and metrics.
    When no config is provided, span() and record_metrics() are safe no-ops
    beyond basic tracing.
    """

    def __init__(
        self,
        config: InstrumentationConfig | None = None,
        *,
        meter: Any | None = None,
        tracer: Any | None = None,
    ) -> None:
        self._config = config or InstrumentationConfig()
        module = self.__class__.__module__
        # Allow dependency injection of meter and tracer for testing.
        self._tracer = tracer if tracer is not None else trace.get_tracer(module)
        self._meter = meter if meter is not None else metrics.get_meter(module)
        self._build_instruments()

    def _build_instruments(self) -> None:
        """Create OTel instruments from the config's timed_spans and metrics dicts.

        Populates _span_histograms for timed span dispatch and _metric_instruments
        for record_metrics dispatch. Called once from __init__.
        """
        self._span_histograms: dict[str, metrics.Histogram] = {
            name: self._meter.create_histogram(
                metric_name, unit=unit or "", description=description
            )
            for name, (
                metric_name,
                unit,
                description,
            ) in self._config.timed_spans.items()
        }
        self._metric_instruments: dict[str, metrics.Histogram | metrics.Counter] = {}
        for key, (kind, metric_name, unit, description) in self._config.metrics.items():
            if kind == "histogram":
                self._metric_instruments[key] = self._meter.create_histogram(
                    metric_name, unit=unit or "", description=description
                )
            else:
                self._metric_instruments[key] = self._meter.create_counter(
                    metric_name, unit=unit or "", description=description
                )

    @contextmanager
    def root_span(self, name: str) -> Generator[None]:
        """Open a named root span for the calling use case.

        Args:
            name: Span name provided by the use case.

        Returns:
            A context manager that opens and closes the root trace span.
        """
        with self._tracer.start_as_current_span(name):
            yield

    @contextmanager
    def span(self, name: str) -> Generator[None]:
        """Open a child span and record its duration if a timed histogram is registered.

        Args:
            name: Identifier for the operation being timed.

        Returns:
            A context manager that records the operation duration on exit.
        """
        histogram = self._span_histograms.get(name)
        with self._tracer.start_as_current_span(name):
            if histogram is not None:
                t0 = time.perf_counter()
                yield
                histogram.record(time.perf_counter() - t0)
            else:
                yield

    def record_metrics(self, data: dict[str, Any]) -> None:
        """Record each key-value pair to its registered OTel instrument.

        Keys not present in _metrics are silently ignored. None values are skipped.

        Args:
            data: Mapping of metric names to their values.
        """
        for key, value in data.items():
            if value is None:
                continue
            instrument = self._metric_instruments.get(key)
            if instrument is None:
                continue
            if hasattr(instrument, "add"):
                instrument.add(value)
            else:
                instrument.record(value)


class SpyInstrumentation(BaseInstrumentation):
    """Test spy that records span names and metrics passed to it."""

    def __init__(self) -> None:
        self.spans: list[str] = []
        self.recorded: dict[str, Any] = {}

    @contextmanager
    def root_span(self, name: str) -> Generator[None]:
        """Record the root span name and yield."""
        self.spans.append(name)
        yield

    @contextmanager
    def span(self, name: str) -> Generator[None]:
        """Record the span name and yield."""
        self.spans.append(name)
        yield

    def record_metrics(self, data: dict[str, Any]) -> None:
        """Merge recorded metrics into the internal dict."""
        self.recorded.update(data)
