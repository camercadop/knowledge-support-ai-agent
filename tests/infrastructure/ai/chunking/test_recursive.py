from app.infrastructure.ai.chunking.recursive import RecursiveChunkStrategy


def _strategy(chunk_size: int = 50, chunk_overlap: int = 10) -> RecursiveChunkStrategy:
    return RecursiveChunkStrategy(chunk_size=chunk_size, chunk_overlap=chunk_overlap)


def test_returns_single_chunk_when_text_fits() -> None:
    assert _strategy().chunk("short text") == ["short text"]


def test_splits_on_paragraph_boundary() -> None:
    text = ("a" * 40 + "\n\n") * 3
    chunks = _strategy(chunk_size=50).chunk(text)
    assert len(chunks) > 1


def test_splits_on_newline_when_no_paragraph_break() -> None:
    text = ("a" * 40 + "\n") * 3
    chunks = _strategy(chunk_size=50).chunk(text)
    assert len(chunks) > 1


def test_falls_back_to_character_split() -> None:
    text = "a" * 200
    chunks = _strategy(chunk_size=50, chunk_overlap=0).chunk(text)
    assert all(len(c) <= 50 for c in chunks)


def test_no_empty_chunks_in_output() -> None:
    text = "word " * 100
    chunks = _strategy(chunk_size=50).chunk(text)
    assert all(c for c in chunks)


def test_overlap_carries_tail_into_next_chunk() -> None:
    text = "a" * 60
    chunks = _strategy(chunk_size=50, chunk_overlap=10).chunk(text)
    assert len(chunks) == 2
    assert chunks[0][-10:] == chunks[1][:10]
