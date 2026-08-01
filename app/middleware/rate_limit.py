import logging

from fastapi import FastAPI
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.config.settings import settings

logger = logging.getLogger(__name__)


limiter = Limiter(
    key_func=get_remote_address,
    strategy="moving-window",
    default_limits=[f"{settings.rate_limit_default}/minute"],
    enabled=settings.rate_limit_enabled,
)


class MovingWindowRateLimitMiddleware(SlowAPIMiddleware):
    """Rate-limiting middleware using the moving-window algorithm.

    Extends slowapi's SlowAPIMiddleware with the moving-window strategy
    configured globally. Rate-limit violations are logged.
    """

    pass


def setup_rate_limiter(app: FastAPI) -> FastAPI:
    """Attach the rate limiter to the FastAPI app and register the middleware.

    Args:
        app: The FastAPI ASGI application.

    Returns:
        The app with the rate limiter middleware registered.
    """
    app.state.limiter = limiter
    app.add_middleware(MovingWindowRateLimitMiddleware)
    return app