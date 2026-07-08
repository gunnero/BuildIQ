"""calculation engine framework

Revision ID: 20260708_0005
Revises: 20260708_0004
Create Date: 2026-07-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260708_0005"
down_revision: Union[str, Sequence[str], None] = "20260708_0004"
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


def created_at() -> sa.Column:
    return sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
    )


def upgrade() -> None:
    op.create_table(
        "calculation_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=True),
        sa.Column("project_task_id", sa.String(length=36), nullable=True),
        sa.Column("room_id", sa.String(length=36), nullable=True),
        sa.Column("measurement_set_id", sa.String(length=36), nullable=True),
        sa.Column("engine_type", sa.String(length=50), nullable=False),
        sa.Column("engine_version", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=36), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["measurement_set_id"], ["measurement_sets.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["project_task_id"], ["project_tasks.id"]),
        sa.ForeignKeyConstraint(["room_id"], ["rooms.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_calculation_runs_company_id", "calculation_runs", ["company_id"])
    op.create_index("ix_calculation_runs_created_by_user_id", "calculation_runs", ["created_by_user_id"])
    op.create_index("ix_calculation_runs_engine_type", "calculation_runs", ["engine_type"])
    op.create_index("ix_calculation_runs_measurement_set_id", "calculation_runs", ["measurement_set_id"])
    op.create_index("ix_calculation_runs_project_id", "calculation_runs", ["project_id"])
    op.create_index("ix_calculation_runs_project_task_id", "calculation_runs", ["project_task_id"])
    op.create_index("ix_calculation_runs_room_id", "calculation_runs", ["room_id"])
    op.create_index("ix_calculation_runs_status", "calculation_runs", ["status"])

    op.create_table(
        "calculation_inputs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("calculation_run_id", sa.String(length=36), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        created_at(),
        sa.ForeignKeyConstraint(["calculation_run_id"], ["calculation_runs.id"]),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_calculation_inputs_calculation_run_id", "calculation_inputs", ["calculation_run_id"])
    op.create_index("ix_calculation_inputs_company_id", "calculation_inputs", ["company_id"])

    op.create_table(
        "calculation_outputs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("calculation_run_id", sa.String(length=36), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        created_at(),
        sa.ForeignKeyConstraint(["calculation_run_id"], ["calculation_runs.id"]),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_calculation_outputs_calculation_run_id", "calculation_outputs", ["calculation_run_id"])
    op.create_index("ix_calculation_outputs_company_id", "calculation_outputs", ["company_id"])

    op.create_table(
        "calculation_line_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=False),
        sa.Column("calculation_run_id", sa.String(length=36), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column("quantity", sa.Float(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        created_at(),
        sa.ForeignKeyConstraint(["calculation_run_id"], ["calculation_runs.id"]),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_calculation_line_items_calculation_run_id",
        "calculation_line_items",
        ["calculation_run_id"],
    )
    op.create_index("ix_calculation_line_items_company_id", "calculation_line_items", ["company_id"])


def downgrade() -> None:
    op.drop_table("calculation_line_items")
    op.drop_table("calculation_outputs")
    op.drop_table("calculation_inputs")
    op.drop_table("calculation_runs")
