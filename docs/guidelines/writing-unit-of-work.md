# Writing a Unit of Work

This document describes how the Unit of Work pattern is implemented and how to extend it.

## Overview

The `UnitOfWork` port is defined in `app/application/shared/ports/unit_of_work.py`. It exposes two methods:

- `get(repo_type)` — resolves and returns the repository instance for the given abstract port, lazily instantiated and cached for the lifetime of the unit of work.
- `commit()` — persists all changes made within the current transaction.

The concrete base implementation is `SqlAlchemyUnitOfWork` in `app/infrastructure/database/sqlalchemy/postgresql/unit_of_work/base.py`. It resolves repositories via the global registry (see `writing-repositories.md`) and caches them in `_cache`.

## Rules

- Never add repository attributes or domain-specific methods to a UoW subclass — all repository access goes through `get()`.
- Never call `commit()` from a repository — only from a use case.
- The `UnitOfWork` port must remain in the application layer; concrete implementations must live in the infrastructure layer.
- Domain subclasses must import the repositories package to ensure all `@repository` decorators run before the first `get()` call.
