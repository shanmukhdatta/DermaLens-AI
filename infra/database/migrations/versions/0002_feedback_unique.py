"""Enforce one unreviewed response per user and completed analysis.

Revision ID: 0002_feedback
Revises: 0001_initial
"""
from __future__ import annotations

from alembic import op

revision = "0002_feedback"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("feedback") as batch:
        batch.create_unique_constraint(
            "uq_feedback_once_per_analysis", ["account_id", "analysis_id"]
        )


def downgrade() -> None:
    with op.batch_alter_table("feedback") as batch:
        batch.drop_constraint("uq_feedback_once_per_analysis", type_="unique")
