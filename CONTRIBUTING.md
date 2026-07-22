# Contributing

Thank you for your interest in contributing. This document covers everything you need to get started.

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Docker & Docker Compose

## Local Setup

```bash
git clone <repo-url>
cd knowledge-support-ai-agent

cp .env.example .env
# Fill in your values

uv sync
docker compose up -d
uv run alembic upgrade head
```

## Branching

- Branch off `dev` for every change.
- Use descriptive branch names: `feat/add-ollama-provider`, `fix/webhook-signature`, `docs/update-adr`.

## Making Changes

This project follows Clean Architecture strictly — business logic is isolated from infrastructure, and every layer has a defined responsibility. Read [docs/guidelines/clean-architecture.md](docs/guidelines/clean-architecture.md) before writing any code.

Before implementing anything non-trivial, check `docs/adr/` for existing architectural decisions and `docs/guidelines/` for how to implement common patterns correctly — violations will be rejected in review.

Follow the conventions in [Development Guide](docs/development.md):

- Google-style docstrings on all new classes and methods.
- Type annotations on all function parameters.
- Use `X | None` instead of `Optional[X]`.
- Module-level logger: `logger = logging.getLogger(__name__)` with `%s`-style formatting.

## Running the Quality Checks

All of these must pass before opening a PR:

```bash
uv run pytest
uv run ruff check .
uv run mypy app/
uv run lint-imports
uv audit --preview-features audit-command
```

`lint-imports` enforces Clean Architecture import boundaries defined in `pyproject.toml`. A violation fails CI.

## Pull Requests

- Keep PRs focused — one concern per PR.
- Write a clear description of what changed and why.
- Reference any related issue in the PR description.
- All CI checks must be green before requesting review.

## Commit Messages

Use the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
feat: add Ollama embedding provider
fix: handle missing phone number in webhook payload
docs: add ADR for provider independence
refactor: extract chunking logic into separate module
test: add unit tests for IngestDocument use case
```

## Adding an ADR

If your change involves an architectural decision, write an ADR before implementing. See [docs/adr/README.md](docs/adr/README.md) for the process and template.
