"""estimate engine

Revision ID: 20260708_0008
Revises: 20260708_0007
Create Date: 2026-07-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260708_0008"
down_revision: Union[str, Sequence[str], None] = "20260708_0007"
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
        "estimates",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("customer_id", sa.String(length=36), nullable=False),
        sa.Column("property_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("estimate_number", sa.String(length=100), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("source_calculation_run_id", sa.String(length=36), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"]),
        sa.ForeignKeyConstraint(["source_calculation_run_id"], ["calculation_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_estimates_company_id", "estimates", ["company_id"])
    op.create_index("ix_estimates_customer_id", "estimates", ["customer_id"])
    op.create_index("ix_estimates_project_id", "estimates", ["project_id"])
    op.create_index("ix_estimates_property_id", "estimates", ["property_id"])
    op.create_index("ix_estimates_source_calculation_run_id", "estimates", ["source_calculation_run_id"])
    op.create_index("ix_estimates_status", "estimates", ["status"])

    op.create_table(
        "estimate_revisions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("estimate_id", sa.String(length=36), nullable=False),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("terms", sa.Text(), nullable=True),
        sa.Column("source_calculation_run_id", sa.String(length=36), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["estimate_id"], ["estimates.id"]),
        sa.ForeignKeyConstraint(["source_calculation_run_id"], ["calculation_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_estimate_revisions_company_id", "estimate_revisions", ["company_id"])
    op.create_index("ix_estimate_revisions_estimate_id", "estimate_revisions", ["estimate_id"])
    op.create_index(
        "ix_estimate_revisions_source_calculation_run_id",
        "estimate_revisions",
        ["source_calculation_run_id"],
    )
    op.create_index("ix_estimate_revisions_status", "estimate_revisions", ["status"])

    op.create_table(
        "estimate_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("estimate_revision_id", sa.String(length=36), nullable=False),
        sa.Column("item_type", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("material_id", sa.String(length=36), nullable=True),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column("unit_price", sa.Float(), nullable=False),
        sa.Column("total_price", sa.Float(), nullable=False),
        sa.Column("source_calculation_run_id", sa.String(length=36), nullable=True),
        sa.Column("source_calculation_line_item_id", sa.String(length=36), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["estimate_revision_id"], ["estimate_revisions.id"]),
        sa.ForeignKeyConstraint(["material_id"], ["materials.id"]),
        sa.ForeignKeyConstraint(["source_calculation_line_item_id"], ["calculation_line_items.id"]),
        sa.ForeignKeyConstraint(["source_calculation_run_id"], ["calculation_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_estimate_items_company_id", "estimate_items", ["company_id"])
    op.create_index("ix_estimate_items_estimate_revision_id", "estimate_items", ["estimate_revision_id"])
    op.create_index("ix_estimate_items_item_type", "estimate_items", ["item_type"])
    op.create_index("ix_estimate_items_material_id", "estimate_items", ["material_id"])
    op.create_index(
        "ix_estimate_items_source_calculation_line_item_id",
        "estimate_items",
        ["source_calculation_line_item_id"],
    )
    op.create_index("ix_estimate_items_source_calculation_run_id", "estimate_items", ["source_calculation_run_id"])


def downgrade() -> None:
    op.drop_table("estimate_items")
    op.drop_table("estimate_revisions")
    op.drop_table("estimates")
