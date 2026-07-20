# models

This package contains the SQLAlchemy ORM models. Every model inherits from `Base` (defined in `database/base.py`), which provides `id` (UUID), `created_at`, and `updated_at` columns.

## Models

| Class | Table | Description |
|-------|-------|-------------|
| `Contact` | `contacts` | A user who interacts with the agent via WhatsApp |
| `Conversation` | `conversations` | A session grouping messages for one contact |
| `Message` | `messages` | A single chat turn within a conversation |
| `Document` | `documents` | A knowledge-base document ingested for RAG |
| `DocumentChunk` | `document_chunks` | A chunk of a document with its pgvector embedding |
