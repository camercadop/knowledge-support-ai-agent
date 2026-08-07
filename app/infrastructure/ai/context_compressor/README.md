# context_compressor

This sub-package implements the `ContextCompressor` port for reducing the number of retrieved chunks before prompt assembly.

## Implementations

- `token_limit.py` — `TokenLimitCompressor`: keeps the highest-ranked chunks (by original retrieval order) until the token budget is exhausted. Use when preserving retrieval relevance order is sufficient.
- `mmr.py` — `MMRCompressor`: selects chunks using Maximal Marginal Relevance, balancing relevance to the query against diversity among already-selected chunks. Use when retrieved chunks are likely to be redundant.

## Configuration

The active strategy is selected via `CONTEXT_COMPRESSION_STRATEGY` (`token_limit`, `mmr`). Compression is opt-in and disabled by default; enable it with `CONTEXT_COMPRESSION_ENABLED=true`. The MMR lambda threshold is controlled by `CONTEXT_COMPRESSION_THRESHOLD` (0.0 = maximum diversity, 1.0 = maximum relevance, default `0.5`).

## Adding a new strategy

1. Create a new module in this package implementing `ContextCompressor`.
2. Export the class from `__init__.py`.
3. Wire it in the container by instantiating it and passing it to `ChunkRetriever.retrieve()`.
