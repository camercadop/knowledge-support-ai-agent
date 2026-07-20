# chat

This sub-package handles the chat use case. `ChatService` orchestrates a full chat turn: it resolves the contact and conversation, retrieves message history, calls the LLM, persists both the user and assistant turns, and returns the reply text to the API layer.

## Responsibilities

- Coordinate repositories, the LLM client, and the database session
- Own the transaction boundary: commit only after all side effects succeed
- Return plain values to the API layer; never expose ORM objects

## Flow

```mermaid
sequenceDiagram
    participant ChatService
    participant ContactRepository
    participant ConversationRepository
    participant MessageRepository
    participant openai_client

    ChatService->>ContactRepository: get_or_create_by_phone(phone)
    ChatService->>ConversationRepository: get_or_create_for_contact(contact_id)
    ChatService->>MessageRepository: list_by_conversation(conversation_id)
    ChatService->>openai_client: chat(history + user_message)
    openai_client-->>ChatService: LLMResponse
    ChatService->>MessageRepository: create(user turn)
    ChatService->>MessageRepository: create(assistant turn)
    ChatService->>DB: commit()
```

## Modules

- `service.py` — `ChatService`; handles a full chat turn end-to-end
