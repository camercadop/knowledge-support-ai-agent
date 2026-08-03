from fastapi import FastAPI

from app.api.analytics import router as analytics_router
from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.api.knowledge_bases import router as knowledge_bases_router
from app.config.logging import configure_logging
from app.config.middlewares import register_middlewares
from app.config.telemetry import setup_telemetry
from app.container import ApplicationContainer

configure_logging()
setup_telemetry()

app = FastAPI(title="Knowledge Support AI Agent")
app.state.container = ApplicationContainer()

register_middlewares(app)

app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(analytics_router)
app.include_router(knowledge_bases_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
