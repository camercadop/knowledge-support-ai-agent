# observability

OTel instrumentation for the application. Contains shared utilities and domain-scoped metric definitions.

## Sub-packages

- `utils.py` — shared helpers, including the `timed_span` context manager for wrapping operations with a span and a latency histogram
- `support/` — OTel instruments for the support domains
