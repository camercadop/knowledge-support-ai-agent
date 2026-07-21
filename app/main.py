from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.config.logging import configure_logging

configure_logging()

app = FastAPI(title="Knowledge Support AI Agent")

app.include_router(chat_router)
app.include_router(documents_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
