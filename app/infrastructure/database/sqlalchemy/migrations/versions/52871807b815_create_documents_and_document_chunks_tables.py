"""create documents and document_chunks tables

Revision ID: bdaf548ef425
Revises: 70a6506dfdc6
Create Date: 2026-08-01 13:23:46.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB

from app.config.settings import settings

_DIMENSIONS = settings.embedding_dimensions or 1536


# revision identifiers, used by Alembic.
revision: str = '52871807b815'
down_revision: Union[str, Sequence[str], None] = '70a6506dfdc6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'documents',
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding_model_used', sa.String(), nullable=True),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('title', 'source', name='uq_documents_title_source'),
    )
    op.create_table(
        'document_chunks',
        sa.Column('document_id', sa.Uuid(), nullable=False),
        sa.Column('chunk', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(_DIMENSIONS), nullable=False),
        sa.Column('metadata', JSONB(), nullable=False, server_default='{}'),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('document_chunks')
    op.drop_table('documents')
