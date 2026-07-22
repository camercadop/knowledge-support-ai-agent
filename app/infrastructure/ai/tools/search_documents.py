from typing import Any

from sqlalchemy.orm import Session

from app.application.ports.embedding_model import EmbeddingModel
from app.application.ports.tool_registry import ToolParameter
from app.application.ports.vector_store import VectorStore
from app.infrastructure.ai.embeddings.openai import OpenAIEmbeddingModel
from app.infrastructure.ai.tools.decorators import tool
from app.infrastructure.vectorstores.pgvector.store import PgVectorStore


@tool(
    name="search_documents",
    description="Search the knowledge base for documents relevant to a query.",
    parameters=[
        ToolParameter(
            name="query",
            type="string",
            description="The search query to look up in the knowledge base.",
        )
    ],
    dependencies={
        "db": None,
        "embedding_model": OpenAIEmbeddingModel,
    },
)
def search_documents_factory(
    db: Session, embedding_model: EmbeddingModel
) -> "SearchDocumentsTool":
    """Construct a SearchDocumentsTool for the given database session and embedding model.

    Args:
        db: The active database session used to back the vector store.
        embedding_model: The embedding model used to embed search queries.

    Returns:
        A SearchDocumentsTool ready to handle tool call arguments.
    """
    return SearchDocumentsTool(
        embedding_model=embedding_model,
        vector_store=PgVectorStore(db),
    )


class SearchDocumentsTool:
    """Tool that retrieves relevant document chunks from the vector store.

    Embeds the query using the provided embedding model and performs a
    similarity search against the vector store. Use this tool when the
    LLM needs to look up information from the knowledge base.
    """

    def __init__(
        self,
        embedding_model: EmbeddingModel,
        vector_store: VectorStore,
    ) -> None:
        """Initialize with the embedding model and vector store to use for retrieval.

        Args:
            embedding_model: Provider used to embed the search query.
            vector_store: Store used to retrieve relevant knowledge chunks.
        """
        self._embedding_model = embedding_model
        self._vector_store = vector_store

    def __call__(self, arguments: dict[str, Any]) -> str:
        """Search the knowledge base for chunks relevant to the given query.

        Args:
            arguments: Must contain a "query" key with the search string.

        Returns:
            Newline-separated list of matching chunks, or a message when none found.
        """
        query: str = arguments["query"]
        embedding = self._embedding_model.embed(query)
        results = self._vector_store.search(embedding)
        if not results:
            return "No relevant documents found."
        return "\n\n".join(r.chunk for r in results)
