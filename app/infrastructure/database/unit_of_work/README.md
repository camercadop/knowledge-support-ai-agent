# unit_of_work

This package contains `UnitOfWork` implementations for the infrastructure layer. Each module provides a concrete backend-specific implementation of the `UnitOfWork` port defined in `app.application.ports.unit_of_work`.

## Modules

- `messaging.py` — `SqlAlchemyMessagingUnitOfWork`: SQLAlchemy-backed implementation for the messaging domain (contacts, conversations, messages)
