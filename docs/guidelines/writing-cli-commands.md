# Writing CLI Commands

This document describes how to implement a CLI command in this project.

## Purpose

CLI commands live in `app/cli/commands/` and are the entry point for terminal interactions. They wire dependencies via `request_context()`, delegate to a use case, and print the result — no business logic.

## Structure

```python
import typer

from app.cli.context import request_context

app = typer.Typer(help="My domain commands.")


@app.command()
def do_something(
    identifier: str = typer.Option(..., prompt=True, help="The identifier."),
) -> None:
    """One-line description shown in --help."""
    with request_context() as (container, db):
        result = container.my_domain.my_use_case(db).handle(identifier)
        typer.echo(result)
```

## Error Handling

Use `typer.echo(..., err=True)` to write to stderr and `raise typer.Exit(code=1)` to signal failure:

```python
@app.command()
def ingest(
    file: str = typer.Option(..., prompt=True, help="Path to the document file."),
) -> None:
    """Ingest a document from a file."""
    path = pathlib.Path(file)
    if not path.exists():
        typer.echo(f"File not found: {file}", err=True)
        raise typer.Exit(code=1)

    with request_context() as (container, db):
        container.support.ingest_document(db).handle(content=path.read_text())
        typer.echo("Done.")
```

## Registering a New Command Group

1. Create `app/cli/commands/<domain>.py` with a `typer.Typer` instance named `app`.
2. Add it to `app/cli/main.py`:

```python
from app.cli.commands import my_domain as my_domain_commands

app.add_typer(my_domain_commands.app)
```

## Output

Use `typer.echo` for user-facing output and `logging` for diagnostics — never mix the two responsibilities:

```python
import logging
import typer

logger = logging.getLogger(__name__)


@app.command()
def do_something(
    identifier: str = typer.Option(..., prompt=True, help="The identifier."),
) -> None:
    """One-line description shown in --help."""
    logger.debug("Running do_something for %s", identifier)
    with request_context() as (container, db):
        result = container.my_domain.my_use_case(db).handle(identifier)
        typer.echo(result)
```

| Concern | Tool |
|---------|------|
| Human-readable result printed to the terminal | `typer.echo` |
| Errors printed to stderr | `typer.echo(..., err=True)` |
| Diagnostics, tracing, observability | `logger` (respects `LOG_LEVEL` and `LOG_FORMAT`) |

Do not use `typer.secho` or `typer.style` — coloured output adds no functional value in this project.

## Rules

- One file per domain under `app/cli/commands/`, named after the domain.
- Every command must use `request_context()` — never instantiate `ApplicationContainer` or `SessionLocal` directly.
- Commands must only wire the use case and print the result — no business logic.
- Always write errors to stderr via `typer.echo(..., err=True)` and exit with `raise typer.Exit(code=1)`.
- All commands must have a docstring — it is displayed as the `--help` description.
- Use `typer.Option(..., prompt=True)` for required inputs so the command is usable both interactively and non-interactively.
- Every module must declare a module-level logger: `logger = logging.getLogger(__name__)`. See [Writing Logs](writing-logs.md).
