-- PostgreSQL Tenant ID Migration Script
-- Add tenant_id support for multi-tenant architecture

\echo 'Starting PostgreSQL tenant_id migration...'

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
\echo '✅ UUID extension enabled'

-- Default tenant UUID
\set DEFAULT_TENANT_ID '00000000-0000-0000-0000-000000000001'

-- Add tenant_id columns to existing tables
\echo 'Adding tenant_id columns...'

ALTER TABLE flow_sesiones ADD COLUMN IF NOT EXISTS tenant_id UUID;
\echo '✅ Added tenant_id to flow_sesiones'

ALTER TABLE flow_pedidos ADD COLUMN IF NOT EXISTS tenant_id UUID;
\echo '✅ Added tenant_id to flow_pedidos'

ALTER TABLE whatsapp_settings ADD COLUMN IF NOT EXISTS tenant_id UUID;
\echo '✅ Added tenant_id to whatsapp_settings'

-- Fill existing records with default tenant_id
\echo 'Updating existing records with default tenant_id...'

UPDATE flow_sesiones SET tenant_id = :'DEFAULT_TENANT_ID'::uuid WHERE tenant_id IS NULL;
\echo '✅ Updated flow_sesiones records'

UPDATE flow_pedidos SET tenant_id = :'DEFAULT_TENANT_ID'::uuid WHERE tenant_id IS NULL;
\echo '✅ Updated flow_pedidos records'

UPDATE whatsapp_settings SET tenant_id = :'DEFAULT_TENANT_ID'::uuid WHERE tenant_id IS NULL;
\echo '✅ Updated whatsapp_settings records'

-- Make tenant_id NOT NULL
\echo 'Making tenant_id columns NOT NULL...'

ALTER TABLE flow_sesiones ALTER COLUMN tenant_id SET NOT NULL;
\echo '✅ flow_sesiones.tenant_id is now NOT NULL'

ALTER TABLE flow_pedidos ALTER COLUMN tenant_id SET NOT NULL;
\echo '✅ flow_pedidos.tenant_id is now NOT NULL'

ALTER TABLE whatsapp_settings ALTER COLUMN tenant_id SET NOT NULL;
\echo '✅ whatsapp_settings.tenant_id is now NOT NULL'

-- Drop existing unique constraint on telefono (if it exists)
\echo 'Handling unique constraints...'

DO $$ 
BEGIN
    -- Drop unique constraint on telefono if it exists
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'flow_sesiones' 
        AND constraint_type = 'UNIQUE' 
        AND constraint_name LIKE '%telefono%'
    ) THEN
        EXECUTE 'ALTER TABLE flow_sesiones DROP CONSTRAINT ' || (
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'flow_sesiones' 
            AND constraint_type = 'UNIQUE' 
            AND constraint_name LIKE '%telefono%'
            LIMIT 1
        );
        RAISE NOTICE '✅ Dropped unique constraint on telefono';
    ELSE
        RAISE NOTICE 'ℹ️  No unique constraint on telefono found';
    END IF;
END $$;

-- Create composite indexes
\echo 'Creating composite indexes...'

-- flow_sesiones: (tenant_id, telefono) UNIQUE
CREATE UNIQUE INDEX IF NOT EXISTS ix_flow_sesiones_tenant_telefono 
ON flow_sesiones (tenant_id, telefono);
\echo '✅ Created ix_flow_sesiones_tenant_telefono'

-- flow_pedidos: (tenant_id, created_at) normal index
CREATE INDEX IF NOT EXISTS ix_flow_pedidos_tenant_created 
ON flow_pedidos (tenant_id, created_at);
\echo '✅ Created ix_flow_pedidos_tenant_created'

-- whatsapp_settings: (tenant_id, provider) UNIQUE
CREATE UNIQUE INDEX IF NOT EXISTS ix_whatsapp_settings_tenant_provider 
ON whatsapp_settings (tenant_id, provider);
\echo '✅ Created ix_whatsapp_settings_tenant_provider'

-- Show summary
\echo 'Migration Summary:'
SELECT 
    'flow_sesiones' as table_name,
    COUNT(*) as total_records,
    COUNT(tenant_id) as records_with_tenant_id
FROM flow_sesiones

UNION ALL

SELECT 
    'flow_pedidos' as table_name,
    COUNT(*) as total_records,
    COUNT(tenant_id) as records_with_tenant_id
FROM flow_pedidos

UNION ALL

SELECT 
    'whatsapp_settings' as table_name,
    COUNT(*) as total_records,
    COUNT(tenant_id) as records_with_tenant_id
FROM whatsapp_settings;

\echo '✅ PostgreSQL tenant_id migration completed successfully!'
\echo 'Default tenant_id: 00000000-0000-0000-0000-000000000001'