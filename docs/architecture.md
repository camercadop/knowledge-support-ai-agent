# Architecture

## Overview

Knowledge Support AI Agent is a FastAPI backend that implements a conversational AI platform using RAG, semantic memory, tool calling, and a layered architecture. WhatsApp Cloud API is the communication channel.

## C4 Level 0 — System Context

```mermaid
flowchart TB
    user["User\n[Person]\nSends chat messages via HTTP"]
    agent["Knowledge Support AI Agent\n[System]\nConversational AI platform with\npersistent chat history"]
    openai["OpenAI\n[External System]\nLLM provider"]
    postgres["PostgreSQL\n[External System]\nPersistent storage"]

    user -->|"POST /chat"| agent
    agent -->|"Chat API"| openai
    agent -->|"Reads/writes data"| postgres
```

## C4 Level 1 — Container

```mermaid
flowchart TB
    user["User\n[Person]"]
    openai["OpenAI\n[External System]"]

    subgraph agent["Knowledge Support AI Agent"]
        api["API Layer\n[FastAPI]\nExposes HTTP endpoints"]
        app["Application Layer\n[Python]\nOrchestrates use cases"]
        infra["Infrastructure\n[Python]\nDB engine and LLM client"]
        db["PostgreSQL\n[Database]\nStores contacts, conversations\nand messages"]
    end

    user -->|"POST /chat"| api
    api --> app
    app --> infra
    infra -->|"Chat API"| openai
    infra -->|"Reads/writes"| db
```

## C4 Level 2 — Component

```mermaid
flowchart TB
    subgraph api["API Layer"]
        chat_router["chat.py\nFastAPI router"]
    end

    subgraph app["Application Layer"]
        use_case["AnswerQuestion\nUse case"]
        port_uow["UnitOfWork\n[port]"]
        port_chat["ChatModel\n[port]"]
    end

    subgraph infra["Infrastructure Layer"]
        sql_uow["SqlAlchemyUnitOfWork"]
        contact_repo["ContactRepository"]
        conv_repo["ConversationRepository"]
        msg_repo["MessageRepository"]
        openai_chat["OpenAIChatModel"]
    end

    subgraph external["External"]
        postgres["PostgreSQL"]
        openai["OpenAI API"]
    end

    chat_router --> use_case
    use_case --> port_uow
    use_case --> port_chat
    port_uow -.->|implements| sql_uow
    port_chat -.->|implements| openai_chat
    sql_uow --> contact_repo
    sql_uow --> conv_repo
    sql_uow --> msg_repo
    contact_repo --> postgres
    conv_repo --> postgres
    msg_repo --> postgres
    openai_chat --> openai
```

## Code Structure

```
app/
    api/              # Route handlers and webhook endpoints
    config/           # Settings and environment configuration
    domain/           # Domain models and business logic
    application/      # Use cases and orchestration
        ports/        # Interfaces for infrastructure dependencies
    infrastructure/   # External integrations (DB, LLM, WhatsApp)
        ai/
            chat/     # Chat completion provider implementations
            embeddings/ # Embedding provider implementations
            mock/     # Mock implementations for testing
        database/     # Models, repositories, and migrations
    schemas/          # Pydantic schemas

tests/
```

## Infrastructure

- PostgreSQL 17 with pgvector extension for vector similarity search.
- Docker Compose manages the local database instance.

## Key Design Decisions

- See `docs/adr/` for all accepted architectural decisions.
