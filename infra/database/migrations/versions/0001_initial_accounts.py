"""Initial privacy-minimal account, consent, analysis and feedback schema.

Revision ID: 0001_initial
Revises:
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, UniqueConstraint

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        Column("id", String(36), primary_key=True),
        Column("issuer", String(512), nullable=False),
        Column("subject", String(255), nullable=False),
        Column("created_at", DateTime(timezone=True), nullable=False),
        UniqueConstraint("issuer", "subject", name="uq_accounts_verified_identity"),
    )
    op.create_table(
        "consents",
        Column("id", String(36), primary_key=True),
        Column(
            "account_id", String(36), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
        ),
        Column("purpose", String(40), nullable=False),
        Column("granted", Boolean, nullable=False),
        Column("updated_at", DateTime(timezone=True), nullable=False),
        UniqueConstraint("account_id", "purpose", name="uq_consent_purpose"),
    )
    op.create_table(
        "analyses",
        Column("id", String(36), primary_key=True),
        Column(
            "account_id", String(36), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
        ),
        Column("status", String(32), nullable=False),
        Column("model_version", String(80)),
        Column("pipeline_version", String(80)),
        Column("created_at", DateTime(timezone=True), nullable=False),
        Column("expires_at", DateTime(timezone=True)),
    )
    op.create_table(
        "feedback",
        Column("id", String(36), primary_key=True),
        Column(
            "account_id", String(36), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
        ),
        Column(
            "analysis_id", String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False
        ),
        Column("choice", String(32), nullable=False),
        Column("review_status", String(32), nullable=False),
        Column("created_at", DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("feedback")
    op.drop_table("analyses")
    op.drop_table("consents")
    op.drop_table("accounts")
