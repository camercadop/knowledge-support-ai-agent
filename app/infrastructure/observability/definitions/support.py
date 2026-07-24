from app.infrastructure.observability.instrumentation import InstrumentationConfig

ANSWER_QUESTION_INSTRUMENTATION = InstrumentationConfig(
    timed_spans={
        "embedding.embed": (
            "rag.embedding_duration_seconds",
            "s",
            "Time spent generating the query embedding",
        ),
        "retrieval.retrieve": (
            "rag.retrieval_duration_seconds",
            "s",
            "Time spent retrieving chunks from the vector store",
        ),
        "llm.generate": (
            "llm.generation_duration_seconds",
            "s",
            "Time spent on the LLM generation call",
        ),
    },
    metrics={
        "rag.chunk_count": (
            "histogram",
            "rag.chunk_count",
            None,
            "Number of chunks included in RAG context per turn",
        ),
        "rag.avg_similarity_score": (
            "histogram",
            "rag.avg_similarity_score",
            None,
            "Average cosine similarity score of retrieved chunks per turn",
        ),
        "llm.input_tokens": (
            "histogram",
            "llm.input_tokens",
            None,
            "Input tokens consumed per turn",
        ),
        "llm.output_tokens": (
            "histogram",
            "llm.output_tokens",
            None,
            "Output tokens consumed per turn",
        ),
        "llm.total_tokens": (
            "histogram",
            "llm.total_tokens",
            None,
            "Total tokens consumed per turn",
        ),
    },
)

INGEST_DOCUMENT_INSTRUMENTATION = InstrumentationConfig(
    timed_spans={
        "ingest.embedding.embed": (
            "ingest.embedding_duration_seconds",
            "s",
            "Time spent embedding a single chunk during ingestion",
        ),
    },
    metrics={
        "ingest.chunk_count": (
            "histogram",
            "ingest.chunk_count",
            None,
            "Number of chunks produced per document ingestion",
        ),
        "ingest.total_chunks_embedded": (
            "counter",
            "ingest.total_chunks_embedded",
            None,
            "Cumulative count of chunks embedded across all ingestions",
        ),
    },
)
