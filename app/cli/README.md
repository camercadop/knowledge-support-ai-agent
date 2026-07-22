# CLI

A Typer-based command-line interface for the Knowledge Support AI Agent. It is a second entry point alongside the HTTP API, consuming the same use cases with manually wired dependencies.

## Commands

| Command | Description |
|---------|-------------|
| `agent chat` | Start an interactive chat REPL for a contact |
| `agent clear-history` | Delete all chat messages for a contact's conversation |
| `agent ingest` | Ingest a document from a file into the knowledge base |

## Usage

```bash
uv run agent --help
uv run agent chat --phone "+1234567890"
uv run agent clear-history --phone "+1234567890"
uv run agent ingest --file ./doc.txt --title "My Doc"
```

All options support `--prompt` fallback: if an option is omitted, the CLI will prompt for it interactively.

## Structure

| File | Responsibility |
|------|----------------|
| `main.py` | Typer app and command definitions |
| `deps.py` | Manual dependency wiring (mirrors `app/api/` without FastAPI DI) |
