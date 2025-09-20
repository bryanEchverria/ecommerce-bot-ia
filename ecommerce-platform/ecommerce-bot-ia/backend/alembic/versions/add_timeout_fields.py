"""Add timeout tracking fields to flow_sesiones

Revision ID: add_timeout_fields
Revises: 
Create Date: 2025-09-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_timeout_fields'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add timeout tracking fields to flow_sesiones table
    try:
        op.add_column('flow_sesiones', sa.Column('last_message_at', sa.DateTime(), nullable=True))
        op.add_column('flow_sesiones', sa.Column('timeout_warning_sent', sa.Boolean(), nullable=True, default=False))
        op.add_column('flow_sesiones', sa.Column('conversation_active', sa.Boolean(), nullable=True, default=True))
        
        # Update existing records with current timestamp
        op.execute("UPDATE flow_sesiones SET last_message_at = updated_at WHERE last_message_at IS NULL")
        op.execute("UPDATE flow_sesiones SET timeout_warning_sent = false WHERE timeout_warning_sent IS NULL")
        op.execute("UPDATE flow_sesiones SET conversation_active = true WHERE conversation_active IS NULL")
        
    except Exception as e:
        print(f"Migration warning: {e}")


def downgrade():
    # Remove timeout tracking fields
    try:
        op.drop_column('flow_sesiones', 'conversation_active')
        op.drop_column('flow_sesiones', 'timeout_warning_sent')
        op.drop_column('flow_sesiones', 'last_message_at')
    except Exception as e:
        print(f"Downgrade warning: {e}")