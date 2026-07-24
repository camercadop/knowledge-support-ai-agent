# Writing Domain Events

This document describes how to define domain events, implement handlers, and wire the event bus in this project.

## Overview

The event bus decouples use cases from cross-domain side effects. After committing a transaction, a use case publishes a domain event. Infrastructure handlers subscribed to that event type react independently — the use case has no knowledge of them.

```
use case  -->  EventPublisher (port)  -->  InMemoryEventBus (impl)  -->  handler(s)
```

The `EventPublisher` port lives in `app/application/shared/events/`. The `InMemoryEventBus` implementation lives in `app/infrastructure/events/`. Handlers live in `app/infrastructure/<domain>/`.

## Defining an Event

Subclass `DomainEvent` in `app/application/<domain>/events/`:

```python
# app/application/support/events/question_answered.py
import uuid
from dataclasses import dataclass

from app.application.shared.events.domain_event import DomainEvent


@dataclass(frozen=True)
class QuestionAnswered(DomainEvent):
    """Raised after a chat turn completes and both messages are persisted."""

    conversation_id: uuid.UUID
    question: str
    answer: str
```

Rules:
- Always frozen dataclasses — events are immutable value objects.
- `occurred_at` is inherited from `DomainEvent` and set automatically.
- Only include data the handler needs — do not embed ORM objects or mutable state.

## Implementing a Handler

Create a handler class in `app/infrastructure/<domain>/event_handlers.py`:

```python
# app/infrastructure/analytics/event_handlers.py
from app.application.analytics.ports.unit_of_work.analytics import AnalyticsUnitOfWork
from app.application.support.events.question_answered import QuestionAnswered


class RagInteractionLogHandler:
    """Persists a RAG interaction log entry when a QuestionAnswered event is received."""

    def __init__(self, uow: AnalyticsUnitOfWork) -> None:
        """Initialize with the analytics unit of work."""
        self._uow = uow

    def handle(self, event: QuestionAnswered) -> None:
        """Persist a RAG interaction log entry from the event payload."""
        self._uow.rag_interaction_logs.create(...)
        self._uow.commit()
```

Rules:
- One handler class per event type per concern.
- Handlers own their own transaction — call `uow.commit()` inside `handle`.
- Handlers must not publish further events.

## Publishing from a Use Case

Inject `EventPublisher` as a constructor dependency and call `publish` after `uow.commit()`:

```python
from app.application.shared.events.event_publisher import EventPublisher

class AnswerQuestion:
    def __init__(self, uow: MessagingUnitOfWork, event_publisher: EventPublisher, ...) -> None:
        self._event_publisher = event_publisher
        ...

    def handle(self, ...) -> AnswerResult:
        ...
        self._uow.commit()
        self._event_publisher.publish(QuestionAnswered(...))
```

Always publish after commit — never before. The event signals that the state change is durable.

## Wiring the Bus

Register handlers on the `InMemoryEventBus` in the container, before building the use case:

```python
# app/container/support.py
event_bus = InMemoryEventBus()
event_bus.register(QuestionAnswered, RagInteractionLogHandler(SqlAlchemyAnalyticsUnitOfWork(db)))

return AnswerQuestion(uow=..., event_publisher=event_bus, ...)
```

A fresh `InMemoryEventBus` is created per request — handlers are registered at construction time and discarded after the request completes.

## Rules

- `DomainEvent`, `EventPublisher`, and `EventHandler` live in `app/application/shared/events/` — never in a domain sub-package.
- Domain-specific events live in `app/application/<domain>/events/`.
- Handlers live in `app/infrastructure/<domain>/` — never in `app/application/`.
- Use cases depend on `EventPublisher` (the port) — never on `InMemoryEventBus` directly.
- Always publish after `uow.commit()` — never inside the transaction.
- Unhandled event types are silently ignored by `InMemoryEventBus`.
