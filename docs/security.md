# Security Controls

This document describes the security controls implemented in the application. Each section covers a specific control, its enforcement mechanism, and the configuration options available.

## CORS Configuration

**Rule:** Cross-origin requests are denied by default. Only explicitly allowed origins may make cross-origin requests.

**Enforcement:** `CORSMiddleware` is mounted in `app/main.py` with the following restrictions:

| Setting | Value |
|---------|-------|
| `allow_origins` | Configured via `CORS_ORIGINS` env var; defaults to empty (deny all) |
| `allow_methods` | `GET`, `POST`, `OPTIONS` |
| `allow_headers` | `Content-Type` |
| `allow_credentials` | `False` |

**Configuration:**

| Environment Variable | Default | Description |
|----------------------|---------|-------------|
| `CORS_ORIGINS` | *(empty)* | Comma-separated list of allowed origins |

**Example:** To allow a frontend at `http://localhost:3000` during development:

```bash
CORS_ORIGINS=http://localhost:3000
```

**Verification:** A request from a non-allowed origin will not receive `Access-Control-Allow-Origin` headers. A request from an allowed origin will receive the header matching the origin value.

## Security Headers

**Rule:** All HTTP responses include security headers that mitigate common web vulnerabilities such as MIME type sniffing, clickjacking, and protocol downgrade attacks.

**Enforcement:** `SecurityHeadersMiddleware` is mounted in `app/main.py` and sets the following headers on every response:

| Header | Default Value |
|--------|---------------|
| `Content-Security-Policy` | `default-src 'none'; frame-ancestors 'none'` |
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |

**Configuration:**

| Environment Variable | Default | Description |
|----------------------|---------|-------------|
| `SECURITY_HEADERS_ENABLED` | `true` | Enable or disable security headers |
| `SECURITY_HEADERS_CONTENT_SECURITY_POLICY` | `default-src 'none'; frame-ancestors 'none'` | Content-Security-Policy header value |
| `SECURITY_HEADERS_X_CONTENT_TYPE_OPTIONS` | `nosniff` | X-Content-Type-Options header value |
| `SECURITY_HEADERS_X_FRAME_OPTIONS` | `DENY` | X-Frame-Options header value |
| `SECURITY_HEADERS_STRICT_TRANSPORT_SECURITY` | `max-age=31536000; includeSubDomains` | Strict-Transport-Security header value |
| `SECURITY_HEADERS_REFERRER_POLICY` | `strict-origin-when-cross-origin` | Referrer-Policy header value |

**Example:** To disable security headers in a development environment:

```bash
SECURITY_HEADERS_ENABLED=false
```

**Verification:** A request to any endpoint returns all five security headers with their configured values. When `SECURITY_HEADERS_ENABLED=false`, the headers are absent from responses.

## Error Handling

**Rule:** Unhandled exceptions must not expose stack traces, internal implementation details, or database errors to clients. Full error details are logged server-side for debugging.

**Enforcement:** `ErrorHandlingMiddleware` is mounted in `app/main.py` via `register_middlewares()` and intercepts all unhandled exceptions at the ASGI level. The middleware catches three categories of exceptions:

| Exception Type | HTTP Status | Client Response |
|----------------|-------------|-----------------|
| `Exception` (unhandled) | `500 Internal Server Error` | `{"error": "Internal server error"}` |
| `HTTPException` | Status code from exception | `{"error": "<detail>"}` |
| `RequestValidationError` | `422 Unprocessable Entity` | `{"error": "Invalid request data"}` |

**Configuration:**

| Environment Variable | Default | Description |
|----------------------|---------|-------------|
| `ERROR_HANDLING_ENABLED` | `true` | Enable or disable error handling middleware |

**Example:** To disable error handling in a development environment:

```bash
ERROR_HANDLING_ENABLED=false
```

**Verification:** A request to an endpoint that raises an unhandled exception returns a `500` response with `{"error": "Internal server error"}` and no stack trace. The full traceback is logged at `ERROR` level via `app.infrastructure.middleware.error_handling`. When `ERROR_HANDLING_ENABLED=false`, exceptions propagate normally and FastAPI's default error responses are returned.

## Input Validation

### Request field constraints

**Rule:** Inbound request fields must enforce length and format bounds to prevent memory exhaustion, unbounded API costs, and malformed data reaching the application layer.

**Enforcement:** Pydantic schema validation in `app/schemas/`:

| Field | Constraint | Enforcement |
|-------|------------|-------------|
| `ChatRequest.phone` | E.164 format, max 15 chars, newlines stripped | `@field_validator` in `app/schemas/chat.py` |
| `ChatRequest.message` | min 1, max 4096 chars | `Field(min_length=1, max_length=4096)` in `app/schemas/chat.py` |
| `DocumentIngestRequest.content` | max 100,000 chars | `Field(max_length=100_000)` in `app/schemas/documents.py` |

**Verification:** A request with a `phone` value not matching E.164 returns `422`. A `content` field exceeding 100,000 characters returns `422`. A `message` field of zero length returns `422`.

### Prompt injection sanitization

**Rule:** User messages must be sanitized before entering the prompt pipeline to neutralize injection directives that attempt to override system instructions.

**Enforcement:** `MessageSanitizer` port (`app/application/support/ports/message_sanitizer.py`) is injected into `AnswerQuestion` and called before the user message is appended to the conversation history. The default adapter is `RegexMessageSanitizer` (`app/infrastructure/ai/message_sanitizer.py`), which applies a configurable list of regex patterns. Multiple sanitizers can be composed via `CompositeSanitizer`.

Sanitization is applied at the application layer, not at the schema layer, because it is a security concern tied to LLM prompt assembly rather than HTTP input formatting.

**Verification:** A message containing a configured injection pattern is stripped or replaced before reaching the LLM. The raw message is persisted to the database unchanged — only the sanitized copy is passed to the prompt pipeline.

## Security Logging

**Rule:** Security-relevant events must be logged using a dedicated security logger (`app.security`) with structured, machine-parseable fields for integration with SIEM or monitoring tools.

**Enforcement:** The `log_security_event()` helper in `app/application/shared/security/logger.py` provides a consistent interface for security audit logging. It attaches structured fields to every log record via the `extra` dict, ensuring that log backends can index and filter security events independently from application logs. Security events are emitted when the message sanitizer rejects input, when rate limits are exceeded, and when request sizes exceed configured bounds.

**Verification:** Security events are logged at `WARNING` level with structured fields. With `LOG_FORMAT=json`, all security events produce structured JSON output parseable by SIEM tools.
