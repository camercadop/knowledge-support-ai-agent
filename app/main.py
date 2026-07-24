from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.config.logging import configure_logging
from app.config.telemetry import setup_telemetry
from app.container import ApplicationContainer

configure_logging()
setup_telemetry()

app = FastAPI(title="Knowledge Support AI Agent")
app.state.container = ApplicationContainer()

app.include_router(chat_router)
app.include_router(documents_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
