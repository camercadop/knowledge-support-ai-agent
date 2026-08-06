"""create_knowledge_base_configs_table

Revision ID: 8bd900f53ec8
Revises: f672609d2e06
Create Date: 2026-08-06 15:11:33.092718

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8bd900f53ec8"
down_revision: Union[str, Sequence[str], None] = "f672609d2e06"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "knowledge_base_configs",
        sa.Column("knowledge_base_id", sa.Uuid(), nullable=False),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["knowledge_base_id"], ["knowledge_bases.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "knowledge_base_id", "key", name="uq_knowledge_base_configs_kb_key"
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("knowledge_base_configs")
