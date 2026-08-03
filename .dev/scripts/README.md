# .dev/scripts

Local development utility scripts. These are not part of the production application and are intended for use during development only.

## Scripts

### dev.py

A Typer CLI application that provides local development utilities.

#### Usage

```bash
uv run python .dev/scripts/dev.py <command>
```

#### Commands

| Command | Description |
|---------|-------------|
| `clear-embeddings` | Delete all documents and their chunks from the database |
| `clear-chats` | Delete all contacts, conversations, and messages from the database |
| `embed-search` | Embed a query and run a raw vector search with no score filter, useful for diagnosing retrieval issues |
| `chat` | Start an interactive stateless chat session with RAG and tool support, or send a single message and exit |

#### Examples

```bash
uv run python .dev/scripts/dev.py clear-embeddings
uv run python .dev/scripts/dev.py embed-search --top-k 5
uv run python .dev/scripts/dev.py chat --message "Hello, what can you help me with?"
```