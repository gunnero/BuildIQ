"""room and measurement engine

Revision ID: 20260708_0004
Revises: 20260708_0003
Create Date: 2026-07-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260708_0004"
down_revision: Union[str, Sequence[str], None] = "20260708_0003"
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
        "rooms",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("project_task_id", sa.String(length=36), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("room_type", sa.String(length=50), nullable=False),
        sa.Column("floor", sa.String(length=100), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("length", sa.Float(), nullable=False),
        sa.Column("width", sa.Float(), nullable=False),
        sa.Column("height", sa.Float(), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["project_task_id"], ["project_tasks.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_rooms_company_id", "rooms", ["company_id"])
    op.create_index("ix_rooms_project_id", "rooms", ["project_id"])
    op.create_index("ix_rooms_project_task_id", "rooms", ["project_task_id"])

    op.create_table(
        "room_openings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("room_id", sa.String(length=36), nullable=False),
        sa.Column("opening_type", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("width", sa.Float(), nullable=False),
        sa.Column("height", sa.Float(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["room_id"], ["rooms.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_room_openings_company_id", "room_openings", ["company_id"])
    op.create_index("ix_room_openings_room_id", "room_openings", ["room_id"])

    op.create_table(
        "measurement_sets",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("project_task_id", sa.String(length=36), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["project_task_id"], ["project_tasks.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_measurement_sets_company_id", "measurement_sets", ["company_id"])
    op.create_index("ix_measurement_sets_project_id", "measurement_sets", ["project_id"])
    op.create_index("ix_measurement_sets_project_task_id", "measurement_sets", ["project_task_id"])

    op.create_table(
        "measurement_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("measurement_set_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["measurement_set_id"], ["measurement_sets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_measurement_items_company_id", "measurement_items", ["company_id"])
    op.create_index("ix_measurement_items_measurement_set_id", "measurement_items", ["measurement_set_id"])


def downgrade() -> None:
    op.drop_table("measurement_items")
    op.drop_table("measurement_sets")
    op.drop_table("room_openings")
    op.drop_table("rooms")
