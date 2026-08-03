from app.infrastructure.ai.chunking.markdown_aware import MarkdownAwareChunkStrategy


def _strategy(chunk_size: int = 80, chunk_overlap: int = 10) -> MarkdownAwareChunkStrategy:
    return MarkdownAwareChunkStrategy(chunk_size=chunk_size, chunk_overlap=chunk_overlap)


def test_returns_single_chunk_when_text_fits() -> None:
    assert _strategy().chunk("short text") == ["short text"]


def test_splits_at_h2_heading_boundary() -> None:
    text = "## Section One\n" + "a" * 60 + "\n## Section Two\n" + "b" * 60
    chunks = _strategy(chunk_size=80).chunk(text)
    assert len(chunks) > 1


def test_splits_at_h3_heading_boundary() -> None:
    text = "### Sub One\n" + "a" * 60 + "\n### Sub Two\n" + "b" * 60
    chunks = _strategy(chunk_size=80).chunk(text)
    assert len(chunks) > 1


def test_falls_back_to_paragraph_split() -> None:
    text = ("a" * 60 + "\n\n") * 3
    chunks = _strategy(chunk_size=80).chunk(text)
    assert len(chunks) > 1


def test_no_empty_chunks_in_output() -> None:
    text = "## A\n" + "word " * 100
    chunks = _strategy(chunk_size=80).chunk(text)
    assert all(c for c in chunks)


def test_falls_back_to_character_split_for_long_words() -> None:
    text = "a" * 300
    chunks = _strategy(chunk_size=80, chunk_overlap=0).chunk(text)
    assert all(len(c) <= 80 for c in chunks)
