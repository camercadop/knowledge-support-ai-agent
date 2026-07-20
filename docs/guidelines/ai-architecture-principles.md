# AI Architecture Principles

This document describes how AI providers (chat, embeddings) are integrated in this project.

## Overview

AI providers are abstracted behind ports in `app/application/ports/`. The application layer depends only on the port — never on a specific SDK. Concrete implementations live in `app/infrastructure/ai/`.

```
app/application/ports/chat_model.py       # ChatModel port
app/application/ports/embedding_model.py  # EmbeddingModel port

app/infrastructure/ai/chat/openai.py      # OpenAI implementation
app/infrastructure/ai/embeddings/openai.py
app/infrastructure/ai/mock/              # Fake implementations for tests
```

## Defining a Port

A port is an abstract class in `app/application/ports/`. It defines the contract the use case depends on:

```python
from abc import ABC, abstractmethod


class ChatModel(ABC):
    """Port that defines the contract for chat completion providers."""

    @abstractmethod
    def generate(self, messages: list[ChatMessage]) -> ChatResponse:
        """Generate a reply for the given message history."""
```

Value objects exchanged through the port (e.g. `ChatMessage`, `ChatResponse`) are defined in the same port module — never imported from infrastructure.

## Implementing a Provider

Create a concrete class in `app/infrastructure/ai/<capability>/`:

```python
from app.application.ports.chat_model import ChatModel, ChatMessage, ChatResponse
from app.config.settings import settings


class OpenAIChatModel(ChatModel):
    """ChatModel implementation backed by the OpenAI Responses API."""

    def __init__(self) -> None:
        """Initialize the OpenAI client from application settings."""
        self._client = OpenAI(api_key=settings.openai_api_key)

    def generate(self, messages: list[ChatMessage]) -> ChatResponse:
        """Send messages to the OpenAI Responses API and return the reply."""
        ...
```

## Provider Selection

The active provider is selected at the router level by instantiating the appropriate implementation. Provider switching requires only a code change in the router — no changes to the use case or port.

For future env-var-driven selection, a factory function in `app/infrastructure/ai/` is the right place.

## Mock Implementations

Fake implementations for tests live in `app/infrastructure/ai/mock/`. They implement the port and return predictable values without making network calls:

```python
class FakeChatModel(ChatModel):
    """Fake ChatModel that returns a fixed reply for use in tests."""

    def generate(self, messages: list[ChatMessage]) -> ChatResponse:
        """Return a fixed assistant reply."""
        return ChatResponse(
            message=ChatMessage(role=Role.ASSISTANT, content="fake reply"),
            usage=TokenUsage(total=None),
        )
```

## Rules

- Use cases must depend on the port, never on a concrete implementation.
- Value objects (e.g. `ChatMessage`) are defined in the port module — not in infrastructure.
- Infrastructure implementations must not import from `app/application/` except for the port they implement.
- One implementation class per provider per capability (e.g. `OpenAIChatModel`, `OpenAIEmbeddingModel`).
- All provider implementations must have a docstring on the class and on every public method.
