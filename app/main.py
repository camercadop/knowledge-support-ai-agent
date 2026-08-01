from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analytics import router as analytics_router
from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.config.logging import configure_logging
from app.config.settings import settings
from app.config.telemetry import setup_telemetry
from app.container import ApplicationContainer

configure_logging()
setup_telemetry()

app = FastAPI(title="Knowledge Support AI Agent")
app.state.container = ApplicationContainer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
    allow_credentials=False,
)

app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(analytics_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
