"""Add consented non-diagnostic result metadata; never image bytes.

Revision ID: 0004_result
Revises: 0003_expiry
"""
from __future__ import annotations

from alembic import op
from sqlalchemy import Column, Text

revision = "0004_result"
down_revision = "0003_expiry"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("analyses", Column("result_json", Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("analyses", "result_json")
