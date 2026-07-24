# mypy: ignore-errors
from dataclasses import dataclass

from opentelemetry import metrics


@dataclass(frozen=True)
class SupportMetrics:
    """OTel histogram instruments for the support domain.

    Holds all histograms recorded during a chat turn. Instantiated once at
    module level and imported by use cases that need to record observability data.

    Attributes:
        embedding_duration: Time spent generating the query embedding.
        retrieval_duration: Time spent retrieving chunks from the vector store.
        llm_duration: Time spent on the LLM generation call.
        chunk_count: Number of chunks included in RAG context per turn.
        avg_similarity_score: Average cosine similarity score of retrieved chunks.
        input_tokens: Input tokens consumed per turn.
        output_tokens: Output tokens consumed per turn.
        total_tokens: Total tokens consumed per turn.
    """

    embedding_duration: metrics.Histogram
    retrieval_duration: metrics.Histogram
    llm_duration: metrics.Histogram
    chunk_count: metrics.Histogram
    avg_similarity_score: metrics.Histogram
    input_tokens: metrics.Histogram
    output_tokens: metrics.Histogram
    total_tokens: metrics.Histogram


def build_support_metrics(meter: metrics.Meter) -> SupportMetrics:
    """Instantiate all support domain histograms from the given meter.

    Args:
        meter: OTel meter used to create the histogram instruments.

    Returns:
        A SupportMetrics instance with all histograms registered.
    """
    return SupportMetrics(
        embedding_duration=meter.create_histogram(
            "rag.embedding_duration_seconds",
            unit="s",
            description="Time spent generating the query embedding",
        ),
        retrieval_duration=meter.create_histogram(
            "rag.retrieval_duration_seconds",
            unit="s",
            description="Time spent retrieving chunks from the vector store",
        ),
        llm_duration=meter.create_histogram(
            "llm.generation_duration_seconds",
            unit="s",
            description="Time spent on the LLM generation call",
        ),
        chunk_count=meter.create_histogram(
            "rag.chunk_count",
            description="Number of chunks included in RAG context per turn",
        ),
        avg_similarity_score=meter.create_histogram(
            "rag.avg_similarity_score",
            description="Average cosine similarity score of retrieved chunks per turn",
        ),
        input_tokens=meter.create_histogram(
            "llm.input_tokens",
            description="Input tokens consumed per turn",
        ),
        output_tokens=meter.create_histogram(
            "llm.output_tokens",
            description="Output tokens consumed per turn",
        ),
        total_tokens=meter.create_histogram(
            "llm.total_tokens",
            description="Total tokens consumed per turn",
        ),
    )


@dataclass(frozen=True)
class IngestMetrics:
    """OTel instruments for the document ingestion use case.

    Attributes:
        embedding_duration: Time spent embedding a single chunk.
        chunk_count: Number of chunks produced per document ingestion.
        total_chunks_embedded: Cumulative count of chunks embedded across all
            ingestions.
    """

    embedding_duration: metrics.Histogram
    chunk_count: metrics.Histogram
    total_chunks_embedded: metrics.Counter


def build_ingest_metrics(meter: metrics.Meter) -> IngestMetrics:
    """Instantiate all ingest domain instruments from the given meter.

    Args:
        meter: OTel meter used to create the instruments.

    Returns:
        An IngestMetrics instance with all instruments registered.
    """
    return IngestMetrics(
        embedding_duration=meter.create_histogram(
            "ingest.embedding_duration_seconds",
            unit="s",
            description="Time spent embedding a single chunk during ingestion",
        ),
        chunk_count=meter.create_histogram(
            "ingest.chunk_count",
            description="Number of chunks produced per document ingestion",
        ),
        total_chunks_embedded=meter.create_counter(
            "ingest.total_chunks_embedded",
            description="Cumulative count of chunks embedded across all ingestions",
        ),
    )
