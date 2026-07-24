import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentChunk:
    """Represents a text chunk of a document in the application layer."""

    id: uuid.UUID
    document_id: uuid.UUID
    chunk: str
