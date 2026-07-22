import typer

from app.cli.context import request_context

app = typer.Typer(help="Support commands.")


@app.command()
def chat(
    phone: str = typer.Option(..., prompt=True, help="Contact phone number."),
) -> None:
    """Start an interactive chat session with a contact.

    Loops until the user types 'exit' or 'quit'.
    """
    with request_context() as (container, db):
        use_case = container.support.answer_question(db)
        typer.echo("Chat started. Type 'exit' to quit.\n")
        while True:
            message = typer.prompt("You")
            if message.strip().lower() in {"exit", "quit"}:
                break
            reply = use_case.handle(phone, message)
            typer.echo(f"Agent: {reply}\n")


@app.command("clear-history")
def clear_history(
    phone: str = typer.Option(..., prompt=True, help="Contact phone number."),
) -> None:
    """Delete all chat messages for a contact's conversation."""
    with request_context() as (container, db):
        container.support.clear_history(db).handle(phone)
        typer.echo("History cleared.")


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
    with request_context() as (container, db):
        document = container.support.ingest_document(db).handle(
            title=title, source=source, content=content
        )
        typer.echo(f"Ingested document {document.id} — {document.title}")
