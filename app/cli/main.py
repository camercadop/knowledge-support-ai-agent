import typer

from app.cli.deps import (
    build_answer_question,
    build_clear_history,
    build_ingest_document,
    get_session,
)
from app.config.logging import configure_logging

configure_logging()

app = typer.Typer(help="Knowledge Support AI Agent CLI.")


@app.command()
def chat(
    phone: str = typer.Option(..., prompt=True, help="Contact phone number."),
) -> None:
    """Start an interactive chat session with a contact.

    Loops until the user types 'exit' or 'quit'.
    """
    db = get_session()
    try:
        use_case = build_answer_question(db)
        typer.echo("Chat started. Type 'exit' to quit.\n")
        while True:
            message = typer.prompt("You")
            if message.strip().lower() in {"exit", "quit"}:
                break
            reply = use_case.handle(phone, message)
            typer.echo(f"Agent: {reply}\n")
    finally:
        db.close()


@app.command("clear-history")
def clear_history(
    phone: str = typer.Option(..., prompt=True, help="Contact phone number."),
) -> None:
    """Delete all chat messages for a contact's conversation."""
    db = get_session()
    try:
        use_case = build_clear_history(db)
        use_case.handle(phone)
        typer.echo("History cleared.")
    finally:
        db.close()


@app.command()
def ingest(
    file: str = typer.Option(..., prompt=True, help="Path to the document file."),
    title: str = typer.Option(..., prompt=True, help="Document title."),
    source: str = typer.Option(default="cli", help="Document source label."),
) -> None:
    """Ingest a document from a file path into the knowledge base."""
    import pathlib

    path = pathlib.Path(file)
    if not path.exists():
        typer.echo(f"File not found: {file}", err=True)
        raise typer.Exit(code=1)

    content = path.read_text(encoding="utf-8")
    db = get_session()
    try:
        use_case = build_ingest_document(db)
        document = use_case.handle(title=title, source=source, content=content)
        typer.echo(f"Ingested document {document.id} — {document.title}")
    finally:
        db.close()
