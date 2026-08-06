"""add_tsvector_to_document_chunks

Revision ID: f672609d2e06
Revises: a1b2c3d4e5f6
Create Date: 2026-08-05 22:45:09.258836

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "f672609d2e06"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add search_vector generated column and GIN index to document_chunks."""
    op.execute("""
        ALTER TABLE document_chunks
        ADD COLUMN search_vector tsvector
        GENERATED ALWAYS AS (to_tsvector('english', chunk)) STORED
    """)
    op.execute("""
        CREATE INDEX ix_document_chunks_search_vector
        ON document_chunks USING GIN (search_vector)
    """)


def downgrade() -> None:
    """Drop search_vector index and column from document_chunks."""
    op.execute("DROP INDEX ix_document_chunks_search_vector")
    op.execute("ALTER TABLE document_chunks DROP COLUMN search_vector")
