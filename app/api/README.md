# api

This package is the HTTP entry point of the application. It contains FastAPI route handlers organized by feature area. Each module defines an `APIRouter` that is mounted in `app.main`. Handlers are intentionally thin: they validate the incoming request via schemas, delegate all business logic to the application layer, and return the serialized response. No domain logic lives here.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/chat` | Receive a user message and return the assistant reply with retrieved chunk metadata |
| `POST` | `/documents` | Ingest a document into the knowledge base |
| `POST` | `/knowledge-bases` | Create a new knowledge base |
| `GET` | `/knowledge-bases` | List all knowledge bases |
| `GET` | `/knowledge-bases/{id}` | Return a knowledge base by id |
| `PATCH` | `/knowledge-bases/{id}` | Partially update a knowledge base |
| `DELETE` | `/knowledge-bases/{id}` | Delete a knowledge base |

## Modules

- `chat.py` — `/chat` endpoint; delegates to `AnswerQuestion`
- `documents.py` — `/documents` endpoint; delegates to `IngestDocument`
- `knowledge_bases.py` — `/knowledge-bases` endpoints; delegates to `KnowledgeBaseCRUD`