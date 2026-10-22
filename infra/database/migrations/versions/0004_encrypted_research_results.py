"""Encrypted nonclinical analysis outcome: no raw-image retention.

Revision ID: 0004_encrypted
Revises: 0003_expiry
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0004_encrypted"
down_revision = "0003_expiry"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("analyses", sa.Column("result_ciphertext", sa.LargeBinary(), nullable=True))


def downgrade() -> None:
    op.drop_column("analyses", "result_ciphertext")
