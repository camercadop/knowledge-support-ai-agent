# unit_of_work

This package contains domain-scoped `UnitOfWork` implementations backed by SQLAlchemy. Each module implements the corresponding port from `app/application/ports/unit_of_work/`.

## Modules

- `messaging.py` — `SqlAlchemyMessagingUnitOfWork`; contacts, conversations, and messages
- `knowledge.py` — `SqlAlchemyKnowledgeUnitOfWork`; documents and document chunks
