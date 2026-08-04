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
