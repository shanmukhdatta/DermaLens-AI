"""Index expiry timestamp for bounded privacy retention operations.

Revision ID: 0003_expiry
Revises: 0002_feedback
"""

from __future__ import annotations

from alembic import op

revision = "0003_expiry"
down_revision = "0002_feedback"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_analyses_expires_at", "analyses", ["expires_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_analyses_expires_at", table_name="analyses")
