# support

This sub-package handles the support use case. `AnswerQuestion` orchestrates a full chat turn: it resolves the contact and conversation, retrieves message history, calls the LLM, persists both the user and assistant turns, and returns the reply text to the API layer.

## Responsibilities

- Coordinate repositories, the LLM client, and the database session
- Own the transaction boundary: commit only after all side effects succeed
- Return plain values to the API layer; never expose ORM objects

## Flow

### AnswerQuestion

```mermaid
sequenceDiagram
    participant UC as AnswerQuestion
    participant Embed as EmbeddingModel
    participant VS as VectorStore
    participant UoW as MessagingUnitOfWork
    participant LLM as ChatModel

    UC->>Embed: embed(user_message)
    Embed-->>UC: query_vector
    UC->>VS: search(query_vector)
    VS-->>UC: chunks (or empty)
    UC->>UoW: contacts.get_or_create_by_phone(phone)
    UC->>UoW: conversations.get_or_create_for_contact(contact_id)
    UC->>UoW: messages.list_by_conversation(conversation_id)
    UC->>LLM: generate(history + user_message, context)
    LLM-->>UC: ChatResponse
    UC->>UoW: messages.create(user turn)
    UC->>UoW: messages.create(assistant turn)
    UC->>UoW: commit()
```

### IngestDocument

```mermaid
sequenceDiagram
    participant UC as IngestDocument
    participant UoW as KnowledgeUnitOfWork
    participant Embed as EmbeddingModel
    participant VS as VectorStore

    UC->>UoW: documents.create(title, source, content)
    loop for each chunk
        UC->>Embed: embed(chunk)
        Embed-->>UC: vector
        UC->>UoW: document_chunks.create(chunk, vector)
        UC->>VS: upsert(chunk_id, document_id, chunk, vector)
    end
    UC->>UoW: commit()
```

## Modules

- `answer_question.py` — `AnswerQuestion`; handles a full chat turn end-to-end
- `ingest_document.py` — `IngestDocument`; chunks, embeds, and indexes a document into the knowledge base
