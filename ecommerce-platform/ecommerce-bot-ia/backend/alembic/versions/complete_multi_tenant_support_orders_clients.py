"""Complete multi-tenant support for orders and clients

Revision ID: complete_multi_tenant_support_orders_clients
Revises: add_tenant_id_multi_tenant_support
Create Date: 2025-09-06 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = 'complete_multi_tenant_support_orders_clients'
down_revision = 'add_tenant_id_multi_tenant_support'
branch_labels = None
depends_on = None

DEFAULT_TENANT_ID = '00000000-0000-0000-0000-000000000001'

def upgrade():
    # Determine database type and client_id column type
    bind = op.get_bind()
    is_postgresql = bind.dialect.name == 'postgresql'
    
    # Define client_id column type based on database
    if is_postgresql:
        client_id_type = UUID(as_uuid=False)
    else:
        client_id_type = sa.String(36)

    # === ADD CLIENT_ID COLUMNS ===
    try:
        # Add client_id to orders table
        op.add_column('orders', sa.Column('client_id', client_id_type, nullable=True))
        
        # Add client_id to clients table  
        op.add_column('clients', sa.Column('client_id', client_id_type, nullable=True))
        
    except Exception as e:
        print(f"Add columns warning: {e}")

    # === MODIFY EMAIL CONSTRAINT IN CLIENTS ===
    try:
        # Drop unique constraint on email in clients (for multi-tenant)
        op.drop_constraint('ix_clients_email', 'clients', type_='unique')
        # Recreate as regular index
        op.create_index('ix_clients_email', 'clients', ['email'], unique=False)
        
    except Exception as e:
        print(f"Modify email constraint warning: {e}")

    # === FILL EXISTING RECORDS WITH DEFAULT TENANT_ID ===
    try:
        # Update existing records with default client_id (tenant_id)
        op.execute(f"UPDATE orders SET client_id = '{DEFAULT_TENANT_ID}' WHERE client_id IS NULL")
        op.execute(f"UPDATE clients SET client_id = '{DEFAULT_TENANT_ID}' WHERE client_id IS NULL")
        
    except Exception as e:
        print(f"Update existing records warning: {e}")

    # === MAKE CLIENT_ID NOT NULL ===
    try:
        # Now make client_id NOT NULL
        op.alter_column('orders', 'client_id', nullable=False)
        op.alter_column('clients', 'client_id', nullable=False)
        
    except Exception as e:
        print(f"Make NOT NULL warning: {e}")

    # === CREATE COMPOSITE INDEXES ===
    try:
        # orders: (client_id, created_at) index for tenant queries
        op.create_index('ix_orders_client_created', 'orders', ['client_id', 'created_at'], unique=False)
        
        # orders: (client_id, order_number) unique for tenant-scoped order numbers
        op.create_index('ix_orders_client_order_number', 'orders', ['client_id', 'order_number'], unique=True)
        
        # clients: (client_id, email) unique for tenant-scoped emails
        op.create_index('ix_clients_client_email', 'clients', ['client_id', 'email'], unique=True)
        
        # clients: (client_id, created_at) index for tenant queries
        op.create_index('ix_clients_client_created', 'clients', ['client_id', 'created_at'], unique=False)
        
    except Exception as e:
        print(f"Create indexes warning: {e}")

    # === DROP GLOBAL UNIQUE CONSTRAINTS ===
    try:
        # Drop global unique constraint on order_number (replace with tenant-scoped)
        op.drop_constraint('ix_orders_order_number', 'orders', type_='unique')
        # Recreate as regular index
        op.create_index('ix_orders_order_number', 'orders', ['order_number'], unique=False)
        
    except Exception as e:
        print(f"Drop global unique constraints warning: {e}")


def downgrade():
    # === RESTORE GLOBAL UNIQUE CONSTRAINTS ===
    try:
        # Restore global unique constraint on order_number
        op.drop_index('ix_orders_order_number', 'orders')
        op.create_index('ix_orders_order_number', 'orders', ['order_number'], unique=True)
        
    except Exception as e:
        print(f"Restore global unique constraints warning: {e}")

    # === DROP COMPOSITE INDEXES ===
    try:
        op.drop_index('ix_clients_client_created', 'clients')
        op.drop_index('ix_clients_client_email', 'clients')
        op.drop_index('ix_orders_client_order_number', 'orders')
        op.drop_index('ix_orders_client_created', 'orders')
        
    except Exception as e:
        print(f"Drop indexes warning: {e}")

    # === RESTORE EMAIL UNIQUE CONSTRAINT ===
    try:
        # Restore unique constraint on email in clients
        op.drop_index('ix_clients_email', 'clients')
        op.create_index('ix_clients_email', 'clients', ['email'], unique=True)
        
    except Exception as e:
        print(f"Restore email constraint warning: {e}")

    # === REMOVE CLIENT_ID COLUMNS ===
    try:
        op.drop_column('clients', 'client_id')
        op.drop_column('orders', 'client_id')
        
    except Exception as e:
        print(f"Drop columns warning: {e}")