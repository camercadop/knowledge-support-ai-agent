# support

This sub-package handles the support use case. `AnswerQuestion` orchestrates a full chat turn: it resolves the contact and conversation, retrieves message history, calls the LLM, persists both the user and assistant turns, and returns the reply text to the API layer.

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

    AnswerQuestion->>ContactRepository: get_or_create_by_phone(phone)
    AnswerQuestion->>ConversationRepository: get_or_create_for_contact(contact_id)
    AnswerQuestion->>MessageRepository: list_by_conversation(conversation_id)
    AnswerQuestion->>openai: chat(history + user_message)
    openai-->>AnswerQuestion: LLMResponse
    AnswerQuestion->>MessageRepository: create(user turn)
    AnswerQuestion->>MessageRepository: create(assistant turn)
    AnswerQuestion->>DB: commit()
```

## Modules

- `answer_question.py` — `AnswerQuestion`; handles a full chat turn end-to-end
