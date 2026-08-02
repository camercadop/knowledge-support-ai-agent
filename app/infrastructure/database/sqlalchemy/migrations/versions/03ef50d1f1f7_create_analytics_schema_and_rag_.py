"""create analytics schema and rag_interaction_logs table

Revision ID: 03ef50d1f1f7
Revises: 52871807b815
Create Date: 2026-08-01 13:23:46.946490

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '03ef50d1f1f7'
down_revision: Union[str, Sequence[str], None] = '52871807b815'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE SCHEMA IF NOT EXISTS analytics")
    op.create_table(
        "rag_interaction_logs",
        sa.Column("conversation_id", sa.Uuid(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("model_used", sa.String(), nullable=False),
        sa.Column("chunks", JSONB(), nullable=True),
        sa.Column("prompt_tokens", sa.Integer(), nullable=True),
        sa.Column("completion_tokens", sa.Integer(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="analytics",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("rag_interaction_logs", schema="analytics")
    op.execute("DROP SCHEMA IF EXISTS analytics")
