# middleware

This package contains ASGI middleware that processes requests before they reach the route handlers.

## Modules

- `security_headers.py` — `SecurityHeadersMiddleware` sets security headers on all HTTP responses.
- `rate_limit.py` — `MovingWindowRateLimitMiddleware` applies rate limiting using the moving-window algorithm via slowapi.
- `request_size_limit.py` — `RequestSizeLimitMiddleware` rejects requests exceeding a configurable body size.
- `error_handling.py` — `ErrorHandlingMiddleware` catches unhandled exceptions and returns safe error responses without exposing stack traces or internal details.

## Security Headers

Security headers are enabled by default and applied to all HTTP responses. The following settings control their values:

| Variable | Default | Description |
|----------|---------|-------------|
| `SECURITY_HEADERS_ENABLED` | `true` | Enable or disable security headers |
| `SECURITY_HEADERS_CONTENT_SECURITY_POLICY` | `default-src 'none'; frame-ancestors 'none'` | Content-Security-Policy header value |
| `SECURITY_HEADERS_X_CONTENT_TYPE_OPTIONS` | `nosniff` | X-Content-Type-Options header value |
| `SECURITY_HEADERS_X_FRAME_OPTIONS` | `DENY` | X-Frame-Options header value |
| `SECURITY_HEADERS_STRICT_TRANSPORT_SECURITY` | `max-age=31536000; includeSubDomains` | Strict-Transport-Security header value |
| `SECURITY_HEADERS_REFERRER_POLICY` | `strict-origin-when-cross-origin` | Referrer-Policy header value |

### Disabling Security Headers

Set `SECURITY_HEADERS_ENABLED=false` in the environment to disable security headers entirely.

## Rate Limiting

Rate limiting is enabled by default and applies a global limit to all endpoints. The global default is configured via `RATE_LIMIT_DEFAULT` in the environment.

### Per-Endpoint Overrides

Individual route handlers can override the global default using the `@limiter.limit()` decorator imported from `app.infrastructure.middleware.rate_limit`. Routes without the decorator use the global `RATE_LIMIT_DEFAULT`.

```python
from app.infrastructure.middleware.rate_limit import limiter

@router.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
def chat(request: ChatRequest, ...) -> ChatResponse:
    ...
```

The limit string format is `<count>/<period>`, where period can be `second`, `minute`, `hour`, or `day`.

### Disabling Rate Limiting

Set `RATE_LIMIT_ENABLED=false` in the environment to disable rate limiting entirely.

## Request Size Limit

Request size limiting is enabled by default and rejects requests whose `Content-Length` header exceeds a configurable size threshold. Requests without a `Content-Length` header (e.g. chunked transfer) are allowed through. Rejected requests receive a `413 Payload Too Large` response.

| Variable | Default | Description |
|----------|---------|-------------|
| `REQUEST_SIZE_LIMIT_DEFAULT` | `1048576` | Maximum request body size in bytes |
| `REQUEST_SIZE_LIMIT_ENABLED` | `true` | Enable or disable request size limiting |

### Disabling Request Size Limiting

Set `REQUEST_SIZE_LIMIT_ENABLED=false` in the environment to disable request size limiting entirely.

## Error Handling

Error handling is enabled by default. The middleware intercepts all unhandled exceptions at the ASGI level and returns safe error responses without exposing stack traces or internal details. Full error details are logged server-side at `ERROR` level for debugging.

### Exception Categories

| Exception Type | HTTP Status | Client Response |
|----------------|-------------|-----------------|
| `Exception` (unhandled) | `500 Internal Server Error` | `{"error": "Internal server error"}` |
| `HTTPException` | Status code from exception | `{"error": "<detail>"}` |
| `RequestValidationError` | `422 Unprocessable Entity` | `{"error": "Invalid request data"}` |

### Configuration

| Environment Variable | Default | Description |
|----------------------|---------|-------------|
| `ERROR_HANDLING_ENABLED` | `true` | Enable or disable error handling middleware |

### Disabling Error Handling

Set `ERROR_HANDLING_ENABLED=false` in the environment to disable error handling entirely. When disabled, exceptions propagate normally and FastAPI's default error responses are returned. This is useful in development environments where detailed error information is helpful for debugging.

### Verification

A request to an endpoint that raises an unhandled exception returns a `500` response with `{"error": "Internal server error"}` and no stack trace or internal details. The full traceback is logged at `ERROR` level via `app.infrastructure.middleware.error_handling`.
