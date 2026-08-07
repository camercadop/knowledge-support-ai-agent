import logging

from app.application.analytics.use_cases.record_rag_interaction import (
    RecordRagInteraction,
)
from app.application.support.events.context_compressed import ContextCompressed
from app.application.support.events.question_answered import QuestionAnswered

logger = logging.getLogger(__name__)


class RagInteractionLogHandler:
    def __init__(self, use_case: RecordRagInteraction) -> None:
        self._use_case = use_case

    def handle(self, event: QuestionAnswered) -> None:
        self._use_case.handle(event)


class CompressionAnalyticsHandler:
    """Logs context compression events for analytics and observability.

    Handles ContextCompressed events emitted by the retrieval pipeline and
    records compression metrics to the application log.
    """

    def handle(self, event: ContextCompressed) -> None:
        """Log compression metrics from a ContextCompressed event.

        Args:
            event: The compression event containing ratio and chunk counts.
        """
        logger.info(
            "context_compressed strategy=%s ratio=%.3f original=%d compressed=%d",
            event.strategy,
            event.compression_ratio,
            event.original_chunk_count,
            event.compressed_chunk_count,
        )
