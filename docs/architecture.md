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

## System Layers

```mermaid
flowchart TB
    client["HTTP Client"]
    api["FastAPI\nAPI Layer"]
    app["Application Layer\nChatService"]
    llm["LLM Provider\nOpenAI Client"]
    repo["Repositories\nContact / Conversation / Message"]
    openai["OpenAI"]
    postgres["PostgreSQL"]

    client -->|"POST /chat"| api
    api --> app
    app --> llm
    app --> repo
    llm --> openai
    repo --> postgres
```

## Code Structure

```
app/
    api/              # Route handlers and webhook endpoints
    core/             # Shared utilities and base classes
    config/           # Settings and environment configuration
    domain/           # Domain models and business logic
    application/      # Use cases and orchestration
    infrastructure/   # External integrations (DB, LLM, WhatsApp)
    repositories/     # Data access layer
    models/           # SQLAlchemy models
    schemas/          # Pydantic schemas
    workers/          # Background tasks

tests/
```

## Infrastructure

- PostgreSQL 17 with pgvector extension for vector similarity search.
- Docker Compose manages the local database instance.

## Key Design Decisions

- See `docs/adr/` for all accepted architectural decisions.
