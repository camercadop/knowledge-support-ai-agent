import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from app.application.support.ports.vector_store import SearchResult

BaseQueryFn = Callable[[uuid.UUID | None, dict[str, str] | None], Any]


@dataclass(frozen=True)
class SearchContext:
    """Base context passed to every SearchStrategy.execute call.

    Carries the inputs that are universal across all retrieval modes.
    Strategy-specific inputs should be captured in a subclass and populated
    by the strategy's own build_context implementation.

    Attributes:
        embedding: Query vector to search against.
        top_k: Maximum number of results to return.
        min_score: If set, exclude results with a score above this threshold.
        knowledge_base_id: If set, scope results to this knowledge base.
        metadata_filters: If set, apply JSONB containment filter on chunk metadata.
        query: Raw query text. Strategies that do not need it may ignore it.
    """

    embedding: list[float]
    top_k: int
    min_score: float | None
    knowledge_base_id: uuid.UUID | None
    metadata_filters: dict[str, str] | None
    query: str | None


class SearchStrategy(ABC):
    """Port that defines a pluggable retrieval strategy for VectorStore.search.

    Each implementation encapsulates one retrieval mode (e.g. vector-only,
    hybrid RRF). The container selects the appropriate implementation at
    startup based on ``settings.retrieval_mode`` via the strategy registry.

    Implementations live in infrastructure/vectorstores/search_strategies/.
    """

    @property
    @abstractmethod
    def mode(self) -> str:
        """Return the retrieval mode identifier this strategy supports.

        Returns:
            A string identifier for the retrieval mode (e.g. ``"vector"``,
            ``"hybrid"``).
        """

    @abstractmethod
    def build_context(
        self,
        embedding: list[float],
        top_k: int,
        min_score: float | None,
        knowledge_base_id: uuid.UUID | None,
        metadata_filters: dict[str, str] | None,
        query: str | None,
    ) -> SearchContext:
        """Build the context object for this strategy's execute call.

        Subclasses may return a SearchContext subclass with additional
        strategy-specific fields populated from constructor-injected settings.

        Args:
            embedding: Query vector to search against.
            top_k: Maximum number of results to return.
            min_score: If set, exclude results with a score above this threshold.
            knowledge_base_id: If set, scope results to this knowledge base.
            metadata_filters: If set, apply JSONB containment filter on chunk metadata.
            query: Raw query text. May be None if no query is available.

        Returns:
            A SearchContext (or subclass) ready to be passed to execute.
        """

    @abstractmethod
    def execute(
        self,
        base_query: BaseQueryFn,
        ctx: SearchContext,
    ) -> list[SearchResult]:
        """Run the retrieval strategy and return ranked results.

        Args:
            base_query: Callable that returns a SQLAlchemy query with the
                common JOIN and filters already applied. Accepts
                (knowledge_base_id, metadata_filters) and returns a Query.
            ctx: Context object produced by build_context for this call.

        Returns:
            List of SearchResult ordered from most to least relevant.
        """
