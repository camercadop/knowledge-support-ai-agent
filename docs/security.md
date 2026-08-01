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