"""material engine

Revision ID: 20260708_0006
Revises: 20260708_0005
Create Date: 2026-07-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260708_0006"
down_revision: Union[str, Sequence[str], None] = "20260708_0005"
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
        "material_categories",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_material_categories_company_id", "material_categories", ["company_id"])

    op.create_table(
        "material_manufacturers",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("website", sa.String(length=500), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_material_manufacturers_company_id",
        "material_manufacturers",
        ["company_id"],
    )

    op.create_table(
        "material_units",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=True),
        sa.Column("key", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_material_units_company_id", "material_units", ["company_id"])
    op.create_index("ix_material_units_key", "material_units", ["key"])

    op.create_table(
        "materials",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("sku", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category_id", sa.String(length=36), nullable=True),
        sa.Column("manufacturer_id", sa.String(length=36), nullable=True),
        sa.Column("unit_id", sa.String(length=36), nullable=False),
        sa.Column("coverage_value", sa.Float(), nullable=True),
        sa.Column("coverage_unit", sa.String(length=50), nullable=True),
        sa.Column("package_quantity", sa.Float(), nullable=True),
        sa.Column("waste_percentage_default", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["category_id"], ["material_categories.id"]),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["manufacturer_id"], ["material_manufacturers.id"]),
        sa.ForeignKeyConstraint(["unit_id"], ["material_units.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_materials_category_id", "materials", ["category_id"])
    op.create_index("ix_materials_company_id", "materials", ["company_id"])
    op.create_index("ix_materials_manufacturer_id", "materials", ["manufacturer_id"])
    op.create_index("ix_materials_unit_id", "materials", ["unit_id"])

    op.create_table(
        "material_consumption_rules",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("material_id", sa.String(length=36), nullable=False),
        sa.Column("engine_type", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("input_unit", sa.String(length=50), nullable=True),
        sa.Column("consumption_rate", sa.Float(), nullable=True),
        sa.Column("waste_percentage", sa.Float(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["material_id"], ["materials.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_material_consumption_rules_company_id",
        "material_consumption_rules",
        ["company_id"],
    )
    op.create_index(
        "ix_material_consumption_rules_engine_type",
        "material_consumption_rules",
        ["engine_type"],
    )
    op.create_index(
        "ix_material_consumption_rules_material_id",
        "material_consumption_rules",
        ["material_id"],
    )


def downgrade() -> None:
    op.drop_table("material_consumption_rules")
    op.drop_table("materials")
    op.drop_table("material_units")
    op.drop_table("material_manufacturers")
    op.drop_table("material_categories")
