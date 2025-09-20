"""Add tenant_id multi-tenant support

Revision ID: add_tenant_id_multi_tenant_support
Revises: add_timeout_fields
Create Date: 2025-01-16 21:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

# revision identifiers, used by Alembic.
revision = 'add_tenant_id_multi_tenant_support'
down_revision = 'add_timeout_fields'
branch_labels = None
depends_on = None

DEFAULT_TENANT_ID = '00000000-0000-0000-0000-000000000001'

def get_tenant_id_column():
    """Return appropriate column type for tenant_id based on database type"""
    # Check if we're using PostgreSQL or SQLite
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        return sa.Column('tenant_id', UUID(as_uuid=False), nullable=True)
    else:
        return sa.Column('tenant_id', sa.String(36), nullable=True)

def upgrade():
    # Determine database type and tenant_id column type
    bind = op.get_bind()
    is_postgresql = bind.dialect.name == 'postgresql'
    
    # Define tenant_id column type based on database
    if is_postgresql:
        tenant_id_type = UUID(as_uuid=False)
        # Enable UUID extension in PostgreSQL
        op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    else:
        tenant_id_type = sa.String(36)

    # === CREATE WHATSAPP_SETTINGS TABLE IF NOT EXISTS ===
    try:
        # Create whatsapp_settings table if it doesn't exist (treating as "credenciales" table)
        op.create_table('whatsapp_settings',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('provider', sa.String(), nullable=False),  # "twilio" o "meta" 
            sa.Column('twilio_account_sid', sa.String(), nullable=True),
            sa.Column('twilio_auth_token', sa.String(), nullable=True),
            sa.Column('twilio_from', sa.String(), nullable=True),
            sa.Column('meta_token', sa.String(), nullable=True),
            sa.Column('meta_phone_number_id', sa.String(), nullable=True),
            sa.Column('meta_graph_api_version', sa.String(), nullable=True, default='v21.0'),
            sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
            sa.Column('tenant_id', tenant_id_type, nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        print("Created whatsapp_settings table")
    except Exception as e:
        print(f"Create table warning: {e}")

    # === ADD TENANT_ID COLUMNS ===
    try:
        # Add tenant_id to flow_sesiones
        op.add_column('flow_sesiones', sa.Column('tenant_id', tenant_id_type, nullable=True))
        
        # Add tenant_id to flow_pedidos  
        op.add_column('flow_pedidos', sa.Column('tenant_id', tenant_id_type, nullable=True))
        
        # tenant_id already added to whatsapp_settings during table creation
        
    except Exception as e:
        print(f"Add columns warning: {e}")

    # === FILL EXISTING RECORDS WITH DEFAULT TENANT_ID ===
    try:
        # Update existing records with default tenant_id
        op.execute(f"UPDATE flow_sesiones SET tenant_id = '{DEFAULT_TENANT_ID}' WHERE tenant_id IS NULL")
        op.execute(f"UPDATE flow_pedidos SET tenant_id = '{DEFAULT_TENANT_ID}' WHERE tenant_id IS NULL")
        # whatsapp_settings is new, no existing records to update
        
    except Exception as e:
        print(f"Update existing records warning: {e}")

    # === MAKE TENANT_ID NOT NULL ===
    try:
        # Now make tenant_id NOT NULL
        op.alter_column('flow_sesiones', 'tenant_id', nullable=False)
        op.alter_column('flow_pedidos', 'tenant_id', nullable=False) 
        op.alter_column('whatsapp_settings', 'tenant_id', nullable=False)
        
    except Exception as e:
        print(f"Make NOT NULL warning: {e}")

    # === REMOVE GLOBAL UNIQUE CONSTRAINTS ===
    try:
        # Drop unique constraint on telefono in flow_sesiones (if it exists)
        # In SQLite, we need to check if constraint exists first
        op.drop_constraint('sqlite_autoindex_flow_sesiones_1', 'flow_sesiones', type_='unique')
        
    except Exception as e:
        print(f"Drop unique constraint warning: {e}")

    # === CREATE COMPOSITE INDEXES ===
    try:
        # flow_sesiones: (tenant_id, telefono) UNIQUE
        op.create_index('ix_flow_sesiones_tenant_telefono', 'flow_sesiones', ['tenant_id', 'telefono'], unique=True)
        
        # flow_pedidos: (tenant_id, created_at) index normal
        op.create_index('ix_flow_pedidos_tenant_created', 'flow_pedidos', ['tenant_id', 'created_at'], unique=False)
        
        # whatsapp_settings: (tenant_id, provider) UNIQUE (treating 'provider' as 'tipo')
        op.create_index('ix_whatsapp_settings_tenant_provider', 'whatsapp_settings', ['tenant_id', 'provider'], unique=True)
        
    except Exception as e:
        print(f"Create indexes warning: {e}")


def downgrade():
    # === DROP COMPOSITE INDEXES ===
    try:
        op.drop_index('ix_whatsapp_settings_tenant_provider', 'whatsapp_settings')
        op.drop_index('ix_flow_pedidos_tenant_created', 'flow_pedidos')
        op.drop_index('ix_flow_sesiones_tenant_telefono', 'flow_sesiones')
        
    except Exception as e:
        print(f"Drop indexes warning: {e}")

    # === RESTORE GLOBAL UNIQUE CONSTRAINTS ===
    try:
        # Restore unique constraint on telefono in flow_sesiones
        op.create_unique_constraint('sqlite_autoindex_flow_sesiones_1', 'flow_sesiones', ['telefono'])
        
    except Exception as e:
        print(f"Restore unique constraint warning: {e}")

    # === REMOVE TENANT_ID COLUMNS ===
    try:
        op.drop_column('flow_pedidos', 'tenant_id')
        op.drop_column('flow_sesiones', 'tenant_id')
        
    except Exception as e:
        print(f"Drop columns warning: {e}")

    # === DROP WHATSAPP_SETTINGS TABLE ===
    try:
        # Drop the entire whatsapp_settings table since we created it
        op.drop_table('whatsapp_settings')
        
    except Exception as e:
        print(f"Drop table warning: {e}")