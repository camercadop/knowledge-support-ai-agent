"""create documents and document_chunks tables

Revision ID: 52871807b815
Revises: 70a6506dfdc6
Create Date: 2026-08-01 12:47:10.033619

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '52871807b815'
down_revision: Union[str, Sequence[str], None] = '70a6506dfdc6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint('uq_documents_title_source', 'documents', ['title', 'source'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_documents_title_source', 'documents', type_='unique')
