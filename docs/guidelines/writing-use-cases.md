# Writing Use Cases

This document describes how to implement a use case in this project. It replaces `writing-application-services.md`.

## Purpose

Use cases live in `app/application/<domain>/` and orchestrate repositories and infrastructure clients to fulfill a single business operation. They own the transaction boundary.

## Structure

```python
import logging

from app.application.ports.chat_model import ChatModel
from app.application.ports.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class DoSomething:
    """Handles the do-something use case."""

    def __init__(self, uow: UnitOfWork, chat_model: ChatModel) -> None:
        """Initialize with a unit of work and required port implementations."""
        self._uow = uow
        self._chat_model = chat_model

    def handle(self, identifier: str, value: str) -> str:
        """Execute the use case and return the result.

        Persists the outcome and commits the transaction.
        """
        entity = self._uow.my_entities.get_or_create(identifier)
        logger.info("Handling use case for entity %s", entity.id)

        result = self._chat_model.generate(...)

        self._uow.my_entities.create(entity.id, value)
        self._uow.commit()
        return result.message.content
```

The caller (route handler or test) constructs and injects the concrete implementations:

```python
# in the router
use_case = DoSomething(uow=SqlAlchemyUnitOfWork(db), chat_model=_chat_model)

# in a test
use_case = DoSomething(uow=FakeUnitOfWork(), chat_model=FakeChatModel())
```

## Unit of Work

Repositories are accessed through the `UnitOfWork` port, not injected individually. This keeps the transaction boundary explicit and testable.

```python
# correct
self._uow.contacts.get_or_create_by_phone(phone)
self._uow.commit()

# wrong — do not inject repositories directly into the use case
```

## Rules

- One class per use case, named after the action (e.g. `AnswerQuestion`, `CreateDocument`).
- File named after the use case in snake_case: `app/application/<domain>/<use_case>.py`.
- The constructor receives a `UnitOfWork` and all other dependencies as port abstractions — never concrete infrastructure types.
- Call `uow.commit()` exactly once, at the end of the use case.
- Never put query logic in a use case — all DB access goes through `uow.<repository>`.
- Use cases may call infrastructure clients (e.g. LLM) through ports but must not be called by them.
- A use case must not import from another use case — shared logic belongs in `app/domain/` or a dedicated service in `app/application/services/`.
