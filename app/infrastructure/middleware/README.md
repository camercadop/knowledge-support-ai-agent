# middleware

This package contains ASGI middleware that processes requests before they reach the route handlers.

## Modules

- `security_headers.py` — `SecurityHeadersMiddleware` sets security headers on all HTTP responses.
- `rate_limit.py` — `MovingWindowRateLimitMiddleware` applies rate limiting using the moving-window algorithm via slowapi.
- `request_size_limit.py` — `RequestSizeLimitMiddleware` rejects requests exceeding a configurable body size.

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
