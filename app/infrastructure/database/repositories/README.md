# repositories

This package contains the SQLAlchemy implementations of the repository ports defined in `application/ports/repositories/`. Each class receives an active `Session` and fulfills the contract of its corresponding abstract base class.

## Implementations

| Class | Port | Table |
|-------|------|-------|
| `ContactRepository` | `AbstractContactRepository` | `contacts` |
| `ConversationRepository` | `AbstractConversationRepository` | `conversations` |
| `MessageRepository` | `AbstractMessageRepository` | `messages` |
| `DocumentChunkRepository` | `AbstractDocumentChunkRepository` | `document_chunks` |
