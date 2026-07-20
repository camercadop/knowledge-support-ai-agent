import logging

from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.config.settings import settings

logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(title="Knowledge Support AI Agent")

app.include_router(chat_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
