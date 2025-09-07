"""Add per-tenant Twilio accounts table

Revision ID: twilio_accounts_001
Revises: complete_multi_tenant_support_orders_clients
Create Date: 2025-09-07 19:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

# revision identifiers, used by Alembic.
revision = 'twilio_accounts_001'
down_revision = 'complete_multi_tenant_support_orders_clients'
branch_labels = None
depends_on = None

def upgrade():
    """Create twilio_accounts table for per-tenant Twilio configurations"""
    op.create_table(
        "twilio_accounts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant_clients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("account_sid", sa.String(64), nullable=False),
        sa.Column("auth_token_enc", sa.LargeBinary(), nullable=False),  # cifrado
        sa.Column("from_number", sa.String(32), nullable=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.UniqueConstraint("tenant_id", name="ux_twilio_accounts_tenant"),
    )

def downgrade():
    """Drop twilio_accounts table"""
    op.drop_table("twilio_accounts")