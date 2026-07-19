from fastapi import FastAPI

app = FastAPI(title="Knowledge Support AI Agent")


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
