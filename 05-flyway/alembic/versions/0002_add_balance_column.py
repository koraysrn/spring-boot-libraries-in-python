"""add balance column

Revision ID: 0002
Revises: 0001
Create Date: 2026-01-02
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    # server_default keeps existing rows valid when the column is added.
    op.add_column(
        "account",
        sa.Column("balance", sa.Float(), nullable=False, server_default="0"),
    )


def downgrade():
    op.drop_column("account", "balance")
