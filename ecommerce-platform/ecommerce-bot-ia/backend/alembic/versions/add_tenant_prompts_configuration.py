"""Add tenant prompts configuration tables

Revision ID: add_tenant_prompts_config
Revises: f1c8a481350d
Create Date: 2025-09-20 06:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_tenant_prompts_config'
down_revision = 'f1c8a481350d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum type for prompt actions
    prompt_action_enum = sa.Enum('CREATE', 'UPDATE', 'ROLLBACK', 'DEACTIVATE', name='promptaction')
    prompt_action_enum.create(op.get_bind())
    
    # Create tenant_prompts table
    op.create_table('tenant_prompts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('system_prompt', sa.Text(), nullable=False),
        sa.Column('style_overrides', postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('nlu_params', postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('nlg_params', postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('version', sa.Integer(), nullable=False, default=1),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('updated_by', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenant_clients.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'version', name='ux_tenant_prompts_tenant_version')
    )
    
    # Create unique index on tenant_id to ensure one active config per tenant
    op.create_index('idx_tenant_prompts_tenant_active', 'tenant_prompts', ['tenant_id', 'is_active'], unique=True, 
                    postgresql_where=sa.text('is_active = true'))
    
    # Create tenant_prompt_audit_log table for change tracking
    op.create_table('tenant_prompt_audit_log',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('prompt_config_id', sa.String(), nullable=False),
        sa.Column('action', prompt_action_enum, nullable=False),
        sa.Column('changes_diff', postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('previous_version', sa.Integer(), nullable=True),
        sa.Column('new_version', sa.Integer(), nullable=True),
        sa.Column('performed_by', sa.String(), nullable=False),
        sa.Column('performed_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenant_clients.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['prompt_config_id'], ['tenant_prompts.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for audit log
    op.create_index('idx_audit_log_tenant_id', 'tenant_prompt_audit_log', ['tenant_id'])
    op.create_index('idx_audit_log_performed_at', 'tenant_prompt_audit_log', ['performed_at'])
    op.create_index('idx_audit_log_action', 'tenant_prompt_audit_log', ['action'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('idx_audit_log_action')
    op.drop_index('idx_audit_log_performed_at') 
    op.drop_index('idx_audit_log_tenant_id')
    op.drop_index('idx_tenant_prompts_tenant_active')
    
    # Drop tables
    op.drop_table('tenant_prompt_audit_log')
    op.drop_table('tenant_prompts')