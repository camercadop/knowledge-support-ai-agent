import uuid
from dataclasses import dataclass
from typing import Any

import sqlalchemy as sa

from app.application.support.ports.search_strategy import (
    BaseQueryFn,
    SearchContext,
    SearchStrategy,
)
from app.application.support.ports.vector_store import SearchResult
from app.config.settings import Settings
from app.infrastructure.database.sqlalchemy.postgresql.models.document_chunk import (
    DocumentChunk as DocumentChunkORM,
)
from app.infrastructure.vectorstores.search_strategies.registry import search_strategy


@search_strategy(mode="vector")
class VectorSearchStrategy(SearchStrategy):  # type: ignore[call-arg]
    """SearchStrategy for pure cosine distance retrieval."""

    def __init__(self, _: Settings) -> None:
        pass

    @property
    def mode(self) -> str:
        return "vector"

    def build_context(
        self,
        embedding: list[float],
        top_k: int,
        min_score: float | None,
        knowledge_base_id: uuid.UUID | None,
        metadata_filters: dict[str, str] | None,
        query: str | None,
    ) -> SearchContext:
        """Build a base SearchContext for vector search.

        Args:
            embedding: Query vector to search against.
            top_k: Maximum number of results to return.
            min_score: If set, exclude results with a cosine distance above this value.
            knowledge_base_id: If set, scope results to this knowledge base.
            metadata_filters: If set, apply JSONB containment filter on chunk metadata.
            query: Ignored by this strategy.

        Returns:
            A SearchContext with the provided values.
        """
        return SearchContext(
            embedding=embedding,
            top_k=top_k,
            min_score=min_score,
            knowledge_base_id=knowledge_base_id,
            metadata_filters=metadata_filters,
            query=query,
        )

    def execute(
        self, base_query: BaseQueryFn, ctx: SearchContext
    ) -> list[SearchResult]:
        """Run a pure cosine distance search and return ranked results.

        Args:
            base_query: Callable returning a SQLAlchemy query with JOIN and
                filters applied.
            ctx: Search context produced by build_context.

        Returns:
            List of SearchResult ordered by cosine distance ascending.
        """
        distance = DocumentChunkORM.embedding.cosine_distance(ctx.embedding).label(
            "distance"
        )
        q = (
            base_query(ctx.knowledge_base_id, ctx.metadata_filters)
            .add_columns(distance)
            .order_by(distance)
        )
        if ctx.min_score is not None:
            q = q.filter(distance <= ctx.min_score)
        rows = q.limit(ctx.top_k).all()
        return [
            SearchResult(
                chunk_id=row.id,
                document_id=row.document_id,
                chunk=row.chunk,
                score=float(dist),
                document_title=title,
                source=source,
                knowledge_base_id=kb_id,
            )
            for row, title, source, kb_id, dist in rows
        ]


@dataclass(frozen=True)
class HybridSearchContext(SearchContext):
    """SearchContext for hybrid vector + full-text search.

    Extends SearchContext with RRF and FTS parameters that are set once at
    strategy construction time and embedded into the context on each call.

    Attributes:
        fts_language: PostgreSQL FTS language configuration name.
        rrf_k: RRF smoothing constant — higher values reduce the impact of
            rank differences between the two ranked lists.
    """

    fts_language: str = "english"
    rrf_k: int = 60


@search_strategy(mode="hybrid")
class HybridSearchStrategy(SearchStrategy):  # type: ignore[call-arg]
    """SearchStrategy for hybrid vector + full-text search fused via RRF."""

    def __init__(self, settings: Settings) -> None:
        self._fts_language = settings.retrieval_hybrid_fts_language
        self._rrf_k = settings.retrieval_hybrid_rrf_k

    @property
    def mode(self) -> str:
        return "hybrid"

    def build_context(
        self,
        embedding: list[float],
        top_k: int,
        min_score: float | None,
        knowledge_base_id: uuid.UUID | None,
        metadata_filters: dict[str, str] | None,
        query: str | None,
    ) -> HybridSearchContext:
        """Build a HybridSearchContext with FTS and RRF settings injected.

        Args:
            embedding: Query vector for the vector search leg.
            top_k: Maximum number of fused results to return.
            min_score: If set, applied as a cosine distance ceiling on the
                vector search leg only.
            knowledge_base_id: If set, scope both legs to this knowledge base.
            metadata_filters: If set, apply JSONB containment filter on both legs.
            query: Raw query text for the full-text search leg.

        Returns:
            A HybridSearchContext with fts_language and rrf_k populated from
            constructor-injected settings.
        """
        return HybridSearchContext(
            embedding=embedding,
            top_k=top_k,
            min_score=min_score,
            knowledge_base_id=knowledge_base_id,
            metadata_filters=metadata_filters,
            query=query,
            fts_language=self._fts_language,
            rrf_k=self._rrf_k,
        )

    def execute(
        self, base_query: BaseQueryFn, ctx: SearchContext
    ) -> list[SearchResult]:
        """Run vector and full-text searches and fuse results with RRF.

        Fetches up to ``top_k * 2`` candidates from each leg to give RRF enough
        signal before the final cap. The score on each returned SearchResult is
        the RRF score (higher is better), not cosine distance.

        Args:
            base_query: Callable returning a SQLAlchemy query with JOIN and
                filters applied.
            ctx: A HybridSearchContext produced by build_context.

        Returns:
            List of SearchResult ordered by RRF score descending.
        """
        assert isinstance(ctx, HybridSearchContext)
        candidate_limit = ctx.top_k * 2

        distance = DocumentChunkORM.embedding.cosine_distance(ctx.embedding).label(
            "distance"
        )
        vector_q = (
            base_query(ctx.knowledge_base_id, ctx.metadata_filters)
            .add_columns(distance)
            .order_by(distance)
        )
        if ctx.min_score is not None:
            vector_q = vector_q.filter(distance <= ctx.min_score)
        vector_rows = vector_q.limit(candidate_limit).all()

        tsquery = sa.func.plainto_tsquery(ctx.fts_language, ctx.query)
        rank = sa.func.ts_rank(DocumentChunkORM.search_vector, tsquery).label("rank")
        fts_rows = (
            base_query(ctx.knowledge_base_id, ctx.metadata_filters)
            .add_columns(rank)
            .filter(DocumentChunkORM.search_vector.op("@@")(tsquery))
            .order_by(rank.desc())
            .limit(candidate_limit)
            .all()
        )

        vector_ranks = {row.id: i for i, (row, *_) in enumerate(vector_rows)}
        fts_ranks = {row.id: i for i, (row, *_) in enumerate(fts_rows)}

        all_rows: dict[uuid.UUID, tuple[Any, str, str | None, uuid.UUID | None]] = {}
        for row, title, source, kb_id, *_ in vector_rows:
            all_rows[row.id] = (row, title, source, kb_id)
        for row, title, source, kb_id, *_ in fts_rows:
            all_rows[row.id] = (row, title, source, kb_id)

        def rrf_score(chunk_id: uuid.UUID) -> float:
            """Compute the RRF score for a chunk across both ranked lists.

            Args:
                chunk_id: UUID of the chunk to score.

            Returns:
                Combined RRF score as a float. Higher is better.
            """
            score = 0.0
            if chunk_id in vector_ranks:
                score += 1.0 / (ctx.rrf_k + vector_ranks[chunk_id])
            if chunk_id in fts_ranks:
                score += 1.0 / (ctx.rrf_k + fts_ranks[chunk_id])
            return score

        ranked = sorted(all_rows.keys(), key=rrf_score, reverse=True)[: ctx.top_k]
        return [
            SearchResult(
                chunk_id=chunk_id,
                document_id=all_rows[chunk_id][0].document_id,
                chunk=all_rows[chunk_id][0].chunk,
                score=rrf_score(chunk_id),
                document_title=all_rows[chunk_id][1],
                source=all_rows[chunk_id][2],
                knowledge_base_id=all_rows[chunk_id][3],
            )
            for chunk_id in ranked
        ]
