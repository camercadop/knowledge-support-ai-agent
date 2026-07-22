# Architecture

## Overview

Knowledge Support AI Agent is a conversational AI platform using RAG, semantic memory, tool calling, and Clean Architecture. It exposes two entry points: a FastAPI HTTP API and a Typer CLI. WhatsApp Cloud API is the intended external communication channel.

## C4 Level 0 — System Context

```mermaid
flowchart TB
    user["User\n[Person]\nSends chat messages via HTTP or CLI"]
    agent["Knowledge Support AI Agent\n[System]\nConversational AI platform with\nRAG and persistent chat history"]
    openai["OpenAI\n[External System]\nLLM and embedding provider"]
    postgres["PostgreSQL + pgvector\n[External System]\nPersistent storage and vector search"]

    user -->|"POST /chat or CLI"| agent
    agent -->|"Chat & Embeddings API"| openai
    agent -->|"Reads/writes data"| postgres
```

## C4 Level 1 — Container

```mermaid
flowchart TB
    user["User\n[Person]"]
    openai["OpenAI\n[External System]"]

    subgraph agent["Knowledge Support AI Agent"]
        api["API Layer\n[FastAPI]\nExposes HTTP endpoints"]
        cli["CLI\n[Typer]\nExposes terminal commands"]
        app["Application Layer\n[Python]\nOrchestrates use cases"]
        infra["Infrastructure\n[Python]\nDB engine, LLM client, vector store, tools"]
        db["PostgreSQL + pgvector\n[Database]\nStores contacts, conversations,\nmessages, documents and embeddings"]
    end

    user -->|"POST /chat"| api
    user -->|"agent chat / ingest"| cli
    api --> app
    cli --> app
    app --> infra
    infra -->|"Chat & Embeddings API"| openai
    infra -->|"Reads/writes"| db
```

## C4 Level 2 — Component

```mermaid
flowchart TB
    subgraph api["API Layer"]
        chat_router["chat.py\nFastAPI router"]
        docs_router["documents.py\nFastAPI router"]
    end

    subgraph cli["CLI Layer"]
        cli_main["main.py\nTyper app"]
    end

    subgraph app["Application Layer"]
        uc_answer["AnswerQuestion\nUse case"]
        uc_ingest["IngestDocument\nUse case"]
        port_msg_uow["MessagingUnitOfWork\n[port]"]
        port_know_uow["KnowledgeUnitOfWork\n[port]"]
        port_chat["ChatModel\n[port]"]
        port_embed["EmbeddingModel\n[port]"]
        port_vs["VectorStore\n[port]"]
        port_tools["ToolRegistry\n[port]"]
        port_prompt["PromptBuilder\n[port]"]
    end

    subgraph infra["Infrastructure Layer"]
        sql_msg_uow["SqlAlchemyMessagingUnitOfWork"]
        sql_know_uow["SqlAlchemyKnowledgeUnitOfWork"]
        contact_repo["ContactRepository"]
        conv_repo["ConversationRepository"]
        msg_repo["MessageRepository"]
        doc_repo["DocumentRepository"]
        chunk_repo["DocumentChunkRepository"]
        openai_chat["OpenAIChatModel"]
        openai_embed["OpenAIEmbeddingModel"]
        pgvector["PgVectorStore"]
        tool_registry["ConcreteToolRegistry"]
        tools["Tools\nget_current_date · search_documents"]
        default_prompt["DefaultPromptBuilder"]
    end

    subgraph external["External"]
        postgres["PostgreSQL + pgvector"]
        openai["OpenAI API"]
    end

    chat_router --> uc_answer
    docs_router --> uc_ingest
    cli_main --> uc_answer
    cli_main --> uc_ingest
    uc_answer --> port_msg_uow
    uc_answer --> port_chat
    uc_answer --> port_tools
    uc_answer --> port_prompt
    uc_ingest --> port_know_uow
    uc_ingest --> port_embed
    uc_ingest --> port_vs
    port_msg_uow -.->|implements| sql_msg_uow
    port_know_uow -.->|implements| sql_know_uow
    port_chat -.->|implements| openai_chat
    port_embed -.->|implements| openai_embed
    port_vs -.->|implements| pgvector
    port_tools -.->|implements| tool_registry
    port_prompt -.->|implements| default_prompt
    tool_registry --> tools
    sql_msg_uow --> contact_repo
    sql_msg_uow --> conv_repo
    sql_msg_uow --> msg_repo
    sql_know_uow --> doc_repo
    sql_know_uow --> chunk_repo
    contact_repo --> postgres
    conv_repo --> postgres
    msg_repo --> postgres
    doc_repo --> postgres
    chunk_repo --> postgres
    pgvector --> postgres
    openai_chat --> openai
    openai_embed --> openai
```

## Code Structure

```
app/
    api/              # Route handlers and webhook endpoints
    application/      # Use cases and orchestration
        models/       # Application-layer value objects
        ports/        # Interfaces for infrastructure dependencies
            repositories/   # One abstract repo per aggregate root
            unit_of_work/   # Domain-scoped transactional boundaries
    cli/              # Typer CLI entry point
    config/           # Settings and environment configuration
    container/        # Composition Root — ApplicationContainer composes domain-scoped containers
    domain/           # Domain models and business logic
    infrastructure/   # External integrations (DB, LLM, WhatsApp)
        ai/
            chat/         # Chat completion provider implementations
            chunking/     # ChunkStrategy implementations
            embeddings/   # Embedding provider implementations
            mock/         # Mock implementations for testing
            prompt_builder/ # PromptBuilder implementations
            tools/        # Tool registry, @tool decorator, and tool implementations
        database/         # ORM adapters, repositories, and migrations
        vectorstores/
            pgvector/   # PgVectorStore — cosine similarity search via pgvector
    schemas/          # Pydantic schemas

tests/
```

## Infrastructure

- PostgreSQL 17 with pgvector extension for vector similarity search.
- Docker Compose manages the local database instance.

## Key Design Decisions

- See `docs/adr/` for all accepted architectural decisions.
