import uuid
from unittest.mock import MagicMock

from app.infrastructure.database.sqlalchemy.postgresql.models.document_chunk import (
    DocumentChunk,
)
from app.infrastructure.vectorstores.pgvector.store import PgVectorStore

_DOC_ID = uuid.uuid4()
_CHUNK_ID = uuid.uuid4()
_EMBEDDING = [0.0] * 1536


def _store() -> tuple[PgVectorStore, MagicMock]:
    db = MagicMock()
    return PgVectorStore(db), db


def test_upsert_adds_new_chunk_when_not_found() -> None:
    store, db = _store()
    db.get.return_value = None

    store.upsert(chunk_id=_CHUNK_ID, document_id=_DOC_ID, chunk="hello", embedding=_EMBEDDING)

    db.add.assert_called_once()
    added: DocumentChunk = db.add.call_args[0][0]
    assert added.id == _CHUNK_ID
    assert added.chunk == "hello"
    assert added.document_id == _DOC_ID


def test_upsert_updates_existing_chunk_when_found() -> None:
    store, db = _store()
    existing = DocumentChunk(
        id=_CHUNK_ID, document_id=_DOC_ID, chunk="old", embedding=_EMBEDDING
    )
    db.get.return_value = existing

    store.upsert(chunk_id=_CHUNK_ID, document_id=_DOC_ID, chunk="new", embedding=_EMBEDDING)

    db.add.assert_not_called()
    assert existing.chunk == "new"


def test_upsert_does_not_call_add_on_update() -> None:
    store, db = _store()
    db.get.return_value = DocumentChunk(
        id=_CHUNK_ID, document_id=_DOC_ID, chunk="x", embedding=_EMBEDDING
    )

    store.upsert(chunk_id=_CHUNK_ID, document_id=_DOC_ID, chunk="y", embedding=_EMBEDDING)

    db.add.assert_not_called()
