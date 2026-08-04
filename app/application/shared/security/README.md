# security

Application-layer security utilities. Provides cross-cutting security concerns that belong in the application layer — not tied to any specific infrastructure, framework, or transport.

## Modules

- `logger.py` — structured security audit logging. Use `log_security_event()` instead of a plain logger call for any security-relevant event (rejected messages, rate limit hits, oversized requests).
