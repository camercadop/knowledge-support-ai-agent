# chunking

This sub-package implements the `ChunkStrategy` port for splitting document text into chunks before embedding and indexing.

## Implementations

- `fixed_size.py` — `FixedSizeChunkStrategy`: splits text into overlapping fixed-character-size windows. Use when document structure is unknown or irrelevant.
- `recursive.py` — `RecursiveChunkStrategy`: splits recursively using a separator hierarchy (`\n\n`, `\n`, `. `, ` `, character). Produces more semantically coherent chunks when structure is present.
- `markdown_aware.py` — `MarkdownAwareChunkStrategy`: extends the recursive approach with Markdown heading separators (`##`, `###`, `####`) at the top of the hierarchy. Use for Markdown documents to keep heading context together with its content.

## Configuration

The active strategy is selected via the `CHUNK_STRATEGY` environment variable (`fixed`, `recursive`, `markdown`). Chunk size and overlap are controlled by `CHUNK_SIZE` and `CHUNK_OVERLAP`.

## Adding a new strategy

1. Create a new module in this package.
2. Decorate the class with `@chunk_strategy("your-name")` imported from `factory.py`.
3. Import the module in `__init__.py` so the decorator runs at startup.
