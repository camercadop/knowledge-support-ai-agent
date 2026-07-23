"""add metadata to document_chunks

Revision ID: a3c2e1f84b57
Revises: f0b1f9d041cd
Create Date: 2026-07-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = "a3c2e1f84b57"
down_revision: Union[str, Sequence[str], None] = "f0b1f9d041cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "document_chunks",
        sa.Column(
            "metadata",
            JSONB,
            nullable=False,
            server_default="{}",
        ),
    )
    op.create_index(
        "ix_document_chunks_metadata",
        "document_chunks",
        ["metadata"],
        postgresql_using="gin",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_document_chunks_metadata", table_name="document_chunks")
    op.drop_column("document_chunks", "metadata")
