import uuid

from pydantic import BaseModel


class DocumentIngestRequest(BaseModel):
    """Payload for ingesting a document into the knowledge base."""

    title: str
    source: str | None = None
    content: str


class DocumentIngestResponse(BaseModel):
    """Response returned after a document is successfully ingested."""

    id: uuid.UUID
    title: str
    source: str | None
