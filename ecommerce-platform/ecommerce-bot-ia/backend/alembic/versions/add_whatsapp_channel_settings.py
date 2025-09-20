"""Add WhatsApp settings table (single tenant)

Revision ID: 9b8c7f3e4d2a
Revises: f1c8a481350d
Create Date: 2025-08-27 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '9b8c7f3e4d2a'
down_revision = 'f1c8a481350d'
branch_labels = None
depends_on = None


def upgrade():
    # Create whatsapp_settings table (single tenant - solo un registro)
    op.create_table(
        'whatsapp_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(), nullable=False),
        
        # Twilio configuration
        sa.Column('twilio_account_sid', sa.String(), nullable=True),
        sa.Column('twilio_auth_token', sa.String(), nullable=True),
        sa.Column('twilio_from', sa.String(), nullable=True),
        
        # Meta configuration
        sa.Column('meta_token', sa.String(), nullable=True),
        sa.Column('meta_phone_number_id', sa.String(), nullable=True),
        sa.Column('meta_graph_api_version', sa.String(), nullable=True, default='v21.0'),
        
        # Status and timestamps
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index
    op.create_index(op.f('ix_whatsapp_settings_id'), 'whatsapp_settings', ['id'])


def downgrade():
    # Drop the table and all associated indexes
    op.drop_index(op.f('ix_whatsapp_settings_id'), table_name='whatsapp_settings')
    op.drop_table('whatsapp_settings')