"""Dev utility scripts for local development.

Usage:
    uv run python .dev/scripts/dev.py clear-embeddings
    uv run python .dev/scripts/dev.py clear-chats
    uv run python .dev/scripts/dev.py embed-search
    uv run python .dev/scripts/dev.py chat
"""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import typer
from prompt_toolkit import prompt as pt_prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.application.support.ports.chat_model import ChatMessage, Role
from app.application.support.services.chunk_retriever import ChunkRetriever
from app.config.logging import configure_logging
from app.config.settings import settings
from app.infrastructure.ai.chat.openai import OpenAIChatModel
from app.infrastructure.ai.embeddings.openai import OpenAIEmbeddingModel
from app.infrastructure.ai.prompt_builder.default import (
    DefaultPromptBuilder,
    PromptConfig,
)
from app.infrastructure.ai.tools.registry import build_tool_registry
from app.infrastructure.database.sqlalchemy.postgresql.engine import (
    SessionLocal,
    engine,
)
from app.infrastructure.vectorstores.pgvector.store import PgVectorStore

app = typer.Typer(help="Local development utilities.")
console = Console()


configure_logging(mode="cli")
logging.getLogger("app").setLevel(logging.DEBUG)
logging.getLogger().setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


@app.command("clear-embeddings")
def clear_embeddings() -> None:
    """Clear all documents and their chunks."""
    with engine.connect() as conn:
        conn.execute(
            text("TRUNCATE document_chunks, documents RESTART IDENTITY CASCADE")
        )
        conn.commit()
    console.print("[green]✓[/green] Embeddings cleared.")


@app.command("clear-chats")
def clear_chats() -> None:
    """Clear all contacts, conversations, and messages."""
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE contacts RESTART IDENTITY CASCADE"))
        conn.commit()
    console.print("[green]✓[/green] Chats cleared.")


@app.command("embed-search")
def embed_search(
    top_k: int = typer.Option(10, help="Number of results to return."),
) -> None:
    """Embed a query and run a raw vector search with no score filter.

    Useful for diagnosing retrieval issues by inspecting actual cosine distances
    before any threshold filtering is applied.
    """
    history = InMemoryHistory()
    style = Style.from_dict({"prompt": "cyan bold"})
    embedding_model = OpenAIEmbeddingModel()

    while True:
        query = pt_prompt("Query: ", history=history, style=style)
        if query.strip().lower() in {"exit", "quit"}:
            break
        if not query.strip():
            continue

        embedding = embedding_model.embed(query)

        db: Session = SessionLocal()
        try:
            results = PgVectorStore(db).search(embedding, top_k=top_k, min_score=None)
        finally:
            db.close()

        if not results:
            console.print("[yellow]No chunks found in the vector store.[/yellow]")
            continue

        table = Table(
            "#", "Distance", "Similarity", "Document", "Chunk", box=None, padding=(0, 1)
        )
        for i, r in enumerate(results, start=1):
            table.add_row(
                str(i),
                f"{r.score:.4f}",
                f"{(1 - r.score) * 100:.1f}%",
                r.document_title,
                r.chunk[:200].replace("\n", " "),
            )
        console.print(table)


@app.command("chat")
def chat(
    message: str | None = typer.Option(
        default=None, help="Send a single message and exit."
    ),
) -> None:
    """Stateless chat simulator with RAG and tool support.

    Each turn embeds the question, retrieves relevant chunks, and calls the LLM
    with the assembled context. No history is accumulated between turns and
    nothing is persisted to the database. When --message is provided, sends
    that single message, prints the result, and exits immediately.
    """
    embedding_model = OpenAIEmbeddingModel()
    prompt_builder = DefaultPromptBuilder(
        config=PromptConfig(
            system_instructions=settings.prompts_system_instructions,
            grounded_instructions=settings.prompts_grounded_instructions,
            no_context_instructions=settings.prompts_no_context_instructions,
        )
    )
    chat_model = OpenAIChatModel(prompt_builder=prompt_builder)

    def _ask(question: str) -> None:
        logger.debug("Embedding question")
        embedding = embedding_model.embed(question)
        logger.debug("Embedding complete, dimensions=%s", len(embedding))

        db: Session = SessionLocal()
        try:
            logger.debug(
                "Retrieving chunks top_k=%s min_score=%s",
                settings.retrieval_top_k,
                settings.retrieval_min_score,
            )
            retrieval = ChunkRetriever(
                vector_store=PgVectorStore(db),
                top_k=settings.retrieval_top_k,
                min_score=settings.retrieval_min_score,
                max_chunks=settings.retrieval_max_chunks,
                max_context_tokens=settings.retrieval_max_context_tokens,
                encoding_name=settings.retrieval_encoding,
            ).retrieve(embedding)
            logger.debug("Retrieved %s chunks", len(retrieval.chunks))
            tool_registry = build_tool_registry(db)
            messages = prompt_builder.build(
                [ChatMessage(role=Role.USER, content=question)],
                retrieval.context,
            )
            logger.debug("Calling LLM model=%s", settings.chat_model)
            response = chat_model.generate(messages, tool_registry=tool_registry)
            logger.debug("LLM response received total_tokens=%s", response.usage.total)
        finally:
            db.close()

        console.print(
            Panel(
                response.message.content,
                title="[green]Agent[/green]",
                border_style="green",
            )
        )

        if retrieval.chunks:
            table = Table(
                "#", "Similarity", "Document", "Chunk", box=None, padding=(0, 1)
            )
            for i, r in enumerate(retrieval.chunks, start=1):
                table.add_row(
                    str(i),
                    f"{(1 - r.score) * 100:.1f}%",
                    r.document_title,
                    r.chunk[:120].replace("\n", " "),
                )
            console.print(
                Panel(table, title="[dim]Citations[/dim]", border_style="dim")
            )

    if message is not None:
        _ask(message)
        return

    history = InMemoryHistory()
    style = Style.from_dict({"prompt": "green bold"})
    while True:
        question = pt_prompt("You: ", history=history, style=style)
        if question.strip().lower() in {"exit", "quit"}:
            break
        if not question.strip():
            continue
        _ask(question)


if __name__ == "__main__":
    app()
