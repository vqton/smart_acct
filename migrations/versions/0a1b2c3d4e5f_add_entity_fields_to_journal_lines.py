"""Add entity_id and entity_name to journal_lines for auto-subsidiary posting

Revision ID: 0a1b2c3d4e5f
Revises: 4fa5b6c7d8e9
Create Date: 2026-07-01 08:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "0a1b2c3d4e5f"
down_revision: Union[str, Sequence[str], None] = "4fa5b6c7d8e9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("journal_lines", sa.Column("entity_id", sa.Integer(), nullable=True, comment="Subsidiary entity ID (customer/vendor/employee etc)"))
    op.add_column("journal_lines", sa.Column("entity_name", sa.String(200), nullable=True, comment="Subsidiary entity name"))
    op.create_index("idx_journal_lines_entity", "journal_lines", ["entity_id"])


def downgrade() -> None:
    op.drop_index("idx_journal_lines_entity", table_name="journal_lines")
    op.drop_column("journal_lines", "entity_name")
    op.drop_column("journal_lines", "entity_id")
