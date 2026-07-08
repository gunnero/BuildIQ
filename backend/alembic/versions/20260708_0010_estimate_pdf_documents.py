"""estimate pdf documents

Revision ID: 20260708_0010
Revises: 20260708_0009
Create Date: 2026-07-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260708_0010"
down_revision: Union[str, Sequence[str], None] = "20260708_0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def timestamps() -> list[sa.Column]:
    return [
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    ]


def upgrade() -> None:
    op.create_table(
        "estimate_documents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("estimate_id", sa.String(length=36), nullable=False),
        sa.Column("revision_id", sa.String(length=36), nullable=False),
        sa.Column("document_type", sa.String(length=100), nullable=False),
        sa.Column("file_path", sa.String(length=1000), nullable=False),
        sa.Column("generated_by_user_id", sa.String(length=36), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["estimate_id"], ["estimates.id"]),
        sa.ForeignKeyConstraint(["generated_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["revision_id"], ["estimate_revisions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_estimate_documents_company_id", "estimate_documents", ["company_id"])
    op.create_index("ix_estimate_documents_document_type", "estimate_documents", ["document_type"])
    op.create_index("ix_estimate_documents_estimate_id", "estimate_documents", ["estimate_id"])
    op.create_index("ix_estimate_documents_generated_by_user_id", "estimate_documents", ["generated_by_user_id"])
    op.create_index("ix_estimate_documents_revision_id", "estimate_documents", ["revision_id"])


def downgrade() -> None:
    op.drop_table("estimate_documents")
