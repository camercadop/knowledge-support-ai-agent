import json

import typer

from app.cli.context import request_context

app = typer.Typer(help="Analytics commands.")


@app.command("export-rag-interactions")
def export_rag_interactions(
    output: str = typer.Option(
        default="-", help="Output file path. Use '-' for stdout."
    ),
) -> None:
    """Export all RAG interaction logs as JSON."""
    with request_context() as (container, db):
        logs = container.support.export_rag_interactions(db).handle()
        data = [
            {
                "id": str(log.id),
                "conversation_id": str(log.conversation_id),
                "question": log.question,
                "answer": log.answer,
                "model_used": log.model_used,
                "chunks": log.chunks,
                "prompt_tokens": log.prompt_tokens,
                "completion_tokens": log.completion_tokens,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ]
        serialized = json.dumps(data, indent=2)
        if output == "-":
            typer.echo(serialized)
        else:
            with open(output, "w", encoding="utf-8") as f:
                f.write(serialized)
            typer.echo(f"Exported {len(data)} records to {output}")
            typer.echo(
                typer.style("✓ Exported ", fg=typer.colors.GREEN, bold=True)
                + typer.style(str(len(data)), bold=True)
                + " records to "
                + typer.style(output, fg=typer.colors.CYAN)
            )
