# models

This package contains the SQLAlchemy ORM models that map to database tables. Each model represents a core domain entity and defines its columns, constraints, and relationships. All models inherit from `Base` (defined in `infrastructure/database/base.py`), which provides a UUID primary key and automatic `created_at` / `updated_at` timestamps.

## Entity relationship

```mermaid
erDiagram
    Contact {
        UUID id PK
        string phone
        string name
        datetime created_at
        datetime updated_at
    }
    Conversation {
        UUID id PK
        UUID contact_id FK
        datetime created_at
        datetime updated_at
    }
    Message {
        UUID id PK
        UUID conversation_id FK
        string role
        text content
        int tokens
        datetime created_at
        datetime updated_at
    }

    Contact ||--o{ Conversation : "has"
    Conversation ||--o{ Message : "contains"
```
