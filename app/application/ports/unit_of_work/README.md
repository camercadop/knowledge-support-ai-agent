# unit_of_work

This package contains one domain-scoped `UnitOfWork` port per bounded context. Each class defines the transactional boundary and exposes only the repositories relevant to its domain. Implementations live in `infrastructure/database/unit_of_work/`.

## Ports

| Class | Domain | Repositories |
|-------|--------|--------------|
| `MessagingUnitOfWork` | Messaging | `contacts`, `conversations`, `messages` |
| `KnowledgeUnitOfWork` | Knowledge | `documents`, `document_chunks` |
