import logging

import typer
from prompt_toolkit import prompt as pt_prompt
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
)
from rich.table import Table

from app.application.support.ports.vector_store import SearchResult
from app.cli.context import request_context

app = typer.Typer(help="Support commands.")
console = Console()


def _citations_table(chunks: list[SearchResult]) -> Table:
    table = Table("#", "Document", "Source", "Similarity", box=None, padding=(0, 1))
    for i, chunk in enumerate(chunks, start=1):
        table.add_row(
            str(i),
            chunk.document_title,
            chunk.source or "—",
            f"{(1 - chunk.score) * 100:.0f}%",
        )
    return table


@app.command()
def chat(
    phone: str = typer.Option(..., prompt=True, help="Contact phone number."),
    message: str | None = typer.Option(
        default=None, help="Send a single message and exit."
    ),
) -> None:
    """Start an interactive chat session with a contact.

    Loops until the user types 'exit' or 'quit'. When --message is provided,
    sends that single message, prints the result, and exits immediately.
    """
    with request_context() as (container, db):
        use_case = container.support.answer_question(db)

        if message is not None:
            result = use_case.handle(phone, message)
            console.print(
                Panel(result.reply, title="[green]Agent[/green]", border_style="green")
            )
            if result.chunks:
                console.print("[dim]Citations:[/dim]")
                console.print(_citations_table(result.chunks))
            return

        console.print(
            Panel(
                "[bold]Knowledge Support AI Agent[/bold]\nType [cyan]exit[/cyan]"
                " or [cyan]quit[/cyan] to end the session.",
                style="blue",
            )
        )
        while True:
            message = pt_prompt(
                "You: ",
                style=Style.from_dict({"prompt": "cyan bold"}),
            )
            if message.strip().lower() in {"exit", "quit"}:
                break
            result = use_case.handle(phone, message)
            console.print(
                Panel(result.reply, title="[green]Agent[/green]", border_style="green")
            )
            if result.chunks:
                console.print("[dim]Citations:[/dim]")
                console.print(_citations_table(result.chunks))
                console.print()


@app.command("clear-history")
def clear_history(
    phone: str = typer.Option(..., prompt=True, help="Contact phone number."),
) -> None:
    """Delete all chat messages for a contact's conversation."""
    with request_context() as (container, db):
        container.support.clear_history(db).handle(phone)
        console.print("[green]✓[/green] History cleared.")


@app.command()
def ingest(
    file: str = typer.Option(..., prompt=True, help="Path to the document file."),
    title: str = typer.Option(..., prompt=True, help="Document title."),
    source: str | None = typer.Option(
        default=None, help="Document source label. Defaults to the file path."
    ),
) -> None:
    """Ingest a document from a file path into the knowledge base."""
    import pathlib

    path = pathlib.Path(file)
    if not path.exists():
        console.print(f"[red]✗ File not found: {file}[/red]")
        raise typer.Exit(code=1)

    content = path.read_text(encoding="utf-8")
    with request_context() as (container, db):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            console=console,
            transient=True,
        ) as progress:
            logging.disable(logging.INFO)
            task = progress.add_task("Embedding chunks…", total=None)

            def on_chunk(current: int, total: int) -> None:
                progress.update(task, total=total, completed=current)

            document = container.support.ingest_document(db).handle(
                title=title,
                source=source or file,
                content=content,
                on_chunk=on_chunk,
            )
            logging.disable(logging.NOTSET)

        console.line()
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_row("[bold]ID[/bold]", str(document.id))
        table.add_row("[bold]Title[/bold]", document.title)
        table.add_row("[bold]Source[/bold]", document.source or "—")
        table.add_row("[bold]Chunks[/bold]", str(document.chunk_count))
        console.print(
            Panel(
                table, title="[green]✓ Document Ingested[/green]", border_style="green"
            )
        )
