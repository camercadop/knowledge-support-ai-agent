# repositories

This package contains one abstract repository per aggregate root. Each class defines the persistence contract that the application layer relies on. Implementations live in `infrastructure/database/repositories/`.

## Abstractions

| Class | Aggregate | Key methods |
|-------|-----------|-------------|
| `AbstractContactRepository` | Contact | `get_or_create_by_phone` |
| `AbstractConversationRepository` | Conversation | `get_or_create_for_contact` |
| `AbstractMessageRepository` | Message | `list_by_conversation`, `create` |
| `AbstractDocumentRepository` | Document | `create`, `get_by_id` |
| `AbstractDocumentChunkRepository` | DocumentChunk | `create` |
