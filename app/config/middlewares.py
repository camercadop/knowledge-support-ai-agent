from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.middleware.security_headers import SecurityHeadersMiddleware


def register_middlewares(app: FastAPI) -> None:
    """Register all application middlewares.

    Centralises middleware wiring so that app/main.py stays focused on
    application bootstrap. Add new middlewares here rather than in main.py.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
        allow_credentials=False,
    )

    app.add_middleware(
        SecurityHeadersMiddleware,
        enabled=settings.security_headers_enabled,
        content_security_policy=settings.security_headers_content_security_policy,
        x_content_type_options=settings.security_headers_x_content_type_options,
        x_frame_options=settings.security_headers_x_frame_options,
        strict_transport_security=settings.security_headers_strict_transport_security,
        referrer_policy=settings.security_headers_referrer_policy,
    )
