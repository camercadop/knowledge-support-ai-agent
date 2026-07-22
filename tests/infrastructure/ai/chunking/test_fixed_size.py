from app.infrastructure.ai.chunking.fixed_size import FixedSizeChunkStrategy


def _strategy() -> FixedSizeChunkStrategy:
    return FixedSizeChunkStrategy(chunk_size=500, chunk_overlap=50)


def test_single_chunk_when_content_fits() -> None:
    assert _strategy().chunk("short") == ["short"]


def test_splits_into_overlapping_chunks() -> None:
    content = "a" * 600
    chunks = _strategy().chunk(content)
    assert len(chunks) == 2
    assert len(chunks[0]) == 500
    assert chunks[1] == content[450:]


def test_overlap_is_shared_between_consecutive_chunks() -> None:
    content = "a" * 1000
    chunks = _strategy().chunk(content)
    assert chunks[0][-50:] == chunks[1][:50]
