"""Add unique constraint for tenant_id + telefono in flow_sesiones

Revision ID: add_unique_flow_sesiones_tenant_phone
Revises: add_tenant_id_multi_tenant_support
Create Date: 2025-09-07 07:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_unique_flow_sesiones_tenant_phone'
down_revision = 'add_tenant_id_multi_tenant_support'
branch_labels = None
depends_on = None

def upgrade():
    """
    Remove global unique constraint on telefono and add composite unique constraint on (tenant_id, telefono)
    """
    # Drop existing unique constraint on telefono if it exists
    try:
        op.drop_index('ix_flow_sesiones_telefono', table_name='flow_sesiones')
    except Exception as e:
        print(f"Could not drop ix_flow_sesiones_telefono index: {e}")
    
    # Create new composite unique index on (tenant_id, telefono)
    op.create_index(
        'ux_flow_sesiones_tenant_phone',
        'flow_sesiones',
        ['tenant_id', 'telefono'],
        unique=True
    )

def downgrade():
    """
    Revert changes: remove composite constraint and restore global unique constraint
    """
    # Drop the composite unique index
    op.drop_index('ux_flow_sesiones_tenant_phone', table_name='flow_sesiones')
    
    # Restore the original unique constraint on telefono (if possible)
    # Note: This might fail if there are duplicate phone numbers across tenants
    try:
        op.create_index('ix_flow_sesiones_telefono', 'flow_sesiones', ['telefono'], unique=True)
    except Exception as e:
        print(f"Warning: Could not restore unique constraint on telefono due to duplicates: {e}")