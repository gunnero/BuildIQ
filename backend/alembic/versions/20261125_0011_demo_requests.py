"""Add demo requests and expiring trial user access."""

from alembic import op
import sqlalchemy as sa


revision = "20261125_0011"
down_revision = "20260708_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("access_expires_at", sa.DateTime(timezone=True)))
    op.create_table(
        "demo_requests",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(254), nullable=False, unique=True),
        sa.Column("company_name", sa.String(120), nullable=False),
        sa.Column("message", sa.String(1000), nullable=False),
        sa.Column("source_key", sa.String(64), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True)),
        sa.Column("approved_by", sa.String(36), sa.ForeignKey("users.id")),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), unique=True),
        sa.Column("activated_at", sa.DateTime(timezone=True)),
        sa.Column("notified_at", sa.DateTime(timezone=True)),
        sa.Column("invitation_sent_at", sa.DateTime(timezone=True)),
        sa.Column("email_attempts", sa.Integer(), nullable=False),
        sa.Column("next_email_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_demo_requests_ip_created", "demo_requests", ["source_key", "created_at"])
    op.create_index("ix_demo_requests_next_email_at", "demo_requests", ["next_email_at"])
    op.execute(sa.text(
        "INSERT INTO subscription_plans "
        "(id, key, name, price_mkd, billing_period, is_active, created_at, updated_at) "
        "VALUES ('e0bb9d22-0000-4800-9000-202611250011', 'demo-trial', 'BuildIQ Demo', "
        "0, 'trial', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
    ))


def downgrade() -> None:
    op.drop_table("demo_requests")
    op.drop_column("users", "access_expires_at")
    op.execute(sa.text(
        "DELETE FROM subscription_plans WHERE key = 'demo-trial' "
        "AND id NOT IN (SELECT plan_id FROM subscriptions)"
    ))
