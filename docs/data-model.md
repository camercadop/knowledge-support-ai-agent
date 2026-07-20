# Data Model

This document describes the conventions and patterns that govern all database models in the project. It is not a per-model inventory — instead, it defines the rules that every model must follow, so the data layer remains consistent as the schema grows.

## Base Model

All models inherit from a shared base class that provides:

- `id` — UUID primary key, generated automatically on insert.
- `created_at` — timestamp set automatically on insert.
- `updated_at` — timestamp set automatically on insert, updated on every change.

## Conventions

- Every model defines its own UUID primary key explicitly — no auto-increment integers.
- Table names are lowercase plural (e.g., `contacts`, `conversations`).
- Foreign keys use `ondelete="CASCADE"` — deleting a parent record removes all dependent records.
- Nullable fields are declared explicitly with `nullable=True`.
- Every field has a comment explaining its purpose.

## Relationships

- Relationships are declared using SQLAlchemy `relationship()` with `back_populates`.
- Circular imports between models are avoided using `TYPE_CHECKING` guards.

## Migrations

- All schema changes are managed through Alembic migrations in `migrations/versions/`.
- Never modify the database schema directly — always generate a migration.
