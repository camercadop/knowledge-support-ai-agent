# Guidelines

How-to references for common development tasks in this project.

## When to Write a Guideline

A guideline is warranted when:

- A recurring implementation pattern needs to be applied consistently across the codebase.
- The correct approach is not obvious from the code alone.
- Developers need step-by-step instructions to implement something correctly.

A guideline is NOT warranted for:

- Architectural decisions — those belong in `docs/adr/`.
- One-off or rarely repeated tasks.
- Anything already self-evident from the existing code.

## Structure

A guideline document must follow this structure:

1. Brief description of what the document covers.
2. Step-by-step instructions with code examples.
3. A `## Rules` section listing non-negotiable constraints, if any.

## Rules

- Filename: `kebab-case.md` (e.g., `writing-repositories.md`).
- Written in English, concise, task-oriented. No background theory — link to the relevant ADR instead.
- Code examples must be minimal and runnable.
- After adding a new guideline, add it to the index below.

## Index

Ordered from foundational to specific — read top to bottom when onboarding.

| Document | Description |
|----------|-------------|
| [Clean Architecture](clean-architecture.md) | How to work within the Clean Architecture, including adding a new domain |
| [Writing Database Models](writing-database-models.md) | How to create a new SQLAlchemy model |
| [Writing Repositories](writing-repositories.md) | How to implement a repository |
| [Writing Use Cases](writing-use-cases.md) | How to implement a use case |
| [Writing API Endpoints](writing-api-endpoints.md) | How to implement a route handler |
| [Dependency Injection](dependency-injection.md) | How dependencies are wired across layers |
| [Error Handling](error-handling.md) | How to handle and translate errors across layers |
| [AI Architecture Principles](ai-architecture-principles.md) | How AI providers are abstracted and wired |
| [Writing Request Schemas](writing-request-schemas.md) | How to define Pydantic request/response schemas |
| [Writing Infrastructure Clients](writing-infrastructure-clients.md) | How to wrap an external SDK or service |
| [Writing Settings](writing-settings.md) | How to add and access application settings |
| [Writing Logs](writing-logs.md) | Logging conventions and formatting rules |
