import uuid
from typing import Any

from app.application.support.ports.embedding_model import EmbeddingModel
from app.application.support.ports.vector_store import SearchResult, VectorStore
from app.infrastructure.ai.tools.search_documents import SearchDocumentsTool


class StubEmbeddingModel(EmbeddingModel):
    """Embedding model stub that returns a fixed vector."""

    def __init__(self, vector: list[float]) -> None:
        """Initialize with the vector to return on every embed call.

        Args:
            vector: The fixed embedding vector to return.
        """
        self._vector = vector

    @property
    def model_name(self) -> str:
        """Return a fixed model name."""
        return "stub"

    def embed(self, text: str) -> list[float]:
        """Return the fixed vector regardless of input.

        Args:
            text: Ignored input text.

        Returns:
            The fixed embedding vector.
        """
        return self._vector


class StubVectorStore(VectorStore):
    """Vector store stub that returns a pre-configured list of results."""

    def __init__(self, results: list[SearchResult]) -> None:
        """Initialize with the results to return on every search call.

        Args:
            results: The fixed list of search results to return.
        """
        self._results = results
        self.last_embedding: list[float] | None = None

    def upsert(
        self,
        chunk_id: uuid.UUID,
        document_id: uuid.UUID,
        chunk: str,
        embedding: list[float],
        metadata: dict[str, str] | None = None,
    ) -> None:
        """No-op upsert for testing purposes."""

    def search(
        self,
        embedding: list[float],
        top_k: int = 5,
        min_score: float | None = None,
        knowledge_base_id: uuid.UUID | None = None,
        metadata_filters: dict[str, str] | None = None,
    ) -> list[SearchResult]:
        """Record the received embedding and return the pre-configured results.

        Args:
            embedding: The query vector passed by the tool.
            top_k: Ignored.
            min_score: Ignored.
            knowledge_base_id: Ignored.
            metadata_filters: Ignored.

        Returns:
            The fixed list of search results.
        """
        self.last_embedding = embedding
        return self._results


def _make_result(chunk: str) -> SearchResult:
    return SearchResult(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        chunk=chunk,
        score=0.1,
        document_title="Doc",
        source=None,
    )


def _make_tool(
    results: list[SearchResult],
) -> tuple[SearchDocumentsTool, StubVectorStore]:
    vector = [1.0, 0.0]
    store = StubVectorStore(results)
    tool = SearchDocumentsTool(
        embedding_model=StubEmbeddingModel(vector),
        vector_store=store,
    )
    return tool, store


def test_call_returns_no_documents_message_when_store_is_empty() -> None:
    tool, _ = _make_tool([])
    result = tool({"query": "anything"})
    assert result == "No relevant documents found."


def test_call_returns_chunk_when_single_result() -> None:
    tool, _ = _make_tool([_make_result("hello world")])
    result = tool({"query": "hello"})
    assert result == "hello world"


def test_call_joins_multiple_chunks_with_double_newline() -> None:
    tool, _ = _make_tool([_make_result("first"), _make_result("second")])
    result = tool({"query": "q"})
    assert result == "first\n\nsecond"


def test_call_passes_embedded_query_to_vector_store() -> None:
    tool, store = _make_tool([])
    tool({"query": "find me"})
    assert store.last_embedding == [1.0, 0.0]
