from fastapi import FastAPI

from app.api.chat import router as chat_router

app = FastAPI(title="Knowledge Support AI Agent")

app.include_router(chat_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
