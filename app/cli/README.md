# CLI

A Typer-based command-line interface for the Knowledge Support AI Agent. It is a second entry point alongside the HTTP API, consuming the same use cases with manually wired dependencies.

## Commands

### support

| Command | Description |
|---------|-------------|
| `agent support chat` | Start an interactive chat REPL for a contact, or send a single message with `--message` |
| `agent support clear-history` | Delete all chat messages for a contact's conversation |
| `agent support ingest` | Ingest a document from a file into the knowledge base |

### analytics

| Command | Description |
|---------|-------------|
| `agent analytics export-rag-interactions` | Export all RAG interaction logs as JSON |

## Usage

```bash
uv run python -m app.cli.main --help
uv run python -m app.cli.main support chat --phone "+1234567890"
uv run python -m app.cli.main support chat --phone "+1234567890" --message "what currencies do you support?"
uv run python -m app.cli.main support clear-history --phone "+1234567890"
uv run python -m app.cli.main support ingest --file ./doc.txt --title "My Doc"
uv run python -m app.cli.main analytics export-rag-interactions
```

All options support `--prompt` fallback: if an option is omitted, the CLI will prompt for it interactively.

## Structure

| File | Responsibility |
|------|----------------|
| `main.py` | Typer app and command definitions |
| `context.py` | Manual dependency wiring (mirrors `app/api/` without FastAPI DI) |
