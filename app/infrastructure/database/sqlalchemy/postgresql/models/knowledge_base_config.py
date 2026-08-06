import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.sqlalchemy.postgresql.base import Base


class KnowledgeBaseConfig(Base):
    """Represents a single configuration key-value entry for a knowledge base."""

    __tablename__ = "knowledge_base_configs"
    __table_args__ = (
        UniqueConstraint(
            "knowledge_base_id", "key", name="uq_knowledge_base_configs_kb_key"
        ),
    )

    knowledge_base_id: Mapped[uuid.UUID] = mapped_column(
        # FK to the owning knowledge base; cascade deletes all config entries
        ForeignKey("knowledge_bases.id", ondelete="CASCADE"),
        nullable=False,
    )
    key: Mapped[str] = mapped_column(
        # Configuration key, e.g. "chat_model" or "retrieval_top_k"
        String,
        nullable=False,
    )
    value: Mapped[str] = mapped_column(
        # Configuration value, always stored as a string
        String,
        nullable=False,
    )
