-- 🏢 MIGRACIÓN PARA AISLAMIENTO MULTI-TENANT
-- Índices compuestos y optimizaciones de performance para consultas por tenant

-- ==========================================
-- 📊 ÍNDICES COMPUESTOS PARA AISLAMIENTO
-- ==========================================

-- 1. PRODUCTOS - Optimizar consultas por tenant
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_client_id_status 
ON products (client_id, status) 
WHERE status IN ('active', 'inactive');

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_client_id_name 
ON products (client_id, name) 
WHERE status = 'active';

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_client_id_category 
ON products (client_id, category) 
WHERE status = 'active';

-- 2. PEDIDOS - Optimizar por tenant y estado
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_client_id_status 
ON orders (client_id, status, created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_client_id_phone 
ON orders (client_id, phone, created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_client_id_date 
ON orders (client_id, created_at DESC) 
WHERE status IN ('pending', 'confirmed', 'delivered');

-- 3. CLIENTES - Optimizar búsquedas por tenant
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_clients_tenant_id_phone 
ON clients (tenant_id, phone) 
WHERE active = true;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_clients_tenant_id_created 
ON clients (tenant_id, created_at DESC);

-- 4. SESIONES DE FLOW - Crítico para bot de WhatsApp
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_flow_sesiones_tenant_telefono 
ON flow_sesiones (tenant_id, telefono, estado);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_flow_sesiones_tenant_updated 
ON flow_sesiones (tenant_id, fecha_actualizacion DESC) 
WHERE estado IN ('activo', 'esperando_respuesta');

-- 5. PRODUCTOS DE FLOW - Para carrito y pedidos
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_flow_products_tenant_active 
ON flow_products (tenant_id, activo) 
WHERE activo = true;

-- 6. CONFIGURACIONES DE WHATSAPP - Por tenant
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_whatsapp_settings_tenant 
ON whatsapp_channel_settings (tenant_id, is_active) 
WHERE is_active = true;

-- 7. CUENTAS DE TWILIO - Multi-provider
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_twilio_accounts_tenant 
ON twilio_accounts (tenant_id, is_active) 
WHERE is_active = true;

-- ==========================================
-- 🔒 CONSTRAINTS PARA INTEGRIDAD DE DATOS
-- ==========================================

-- Asegurar que tenant_id no sea null en tablas críticas
ALTER TABLE products ADD CONSTRAINT chk_products_client_id_not_null 
CHECK (client_id IS NOT NULL AND client_id != '');

ALTER TABLE orders ADD CONSTRAINT chk_orders_client_id_not_null 
CHECK (client_id IS NOT NULL AND client_id != '');

ALTER TABLE flow_sesiones ADD CONSTRAINT chk_flow_sesiones_tenant_not_null 
CHECK (tenant_id IS NOT NULL AND tenant_id != '');

ALTER TABLE flow_products ADD CONSTRAINT chk_flow_products_tenant_not_null 
CHECK (tenant_id IS NOT NULL AND tenant_id != '');

-- ==========================================
-- 📋 TABLA DE AUDITORÍA PARA RESOLUCIÓN DE TENANTS
-- ==========================================

CREATE TABLE IF NOT EXISTS tenant_resolution_audit (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    tenant_id VARCHAR(255),
    resolution_method VARCHAR(50) NOT NULL, -- 'subdomain', 'header', 'query', 'rejected'
    status VARCHAR(50) NOT NULL, -- 'success', 'error', 'rejected', 'no_tenant'
    duration_ms NUMERIC(10,2),
    request_info JSONB,
    error_detail TEXT,
    
    -- Índices para consultas de auditoría
    INDEX (timestamp DESC, tenant_id),
    INDEX (tenant_id, status, timestamp DESC),
    INDEX (resolution_method, status)
);

-- Particionamiento por fecha para performance
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tenant_audit_date 
ON tenant_resolution_audit (DATE(timestamp), tenant_id);

-- ==========================================
-- 📊 TABLA DE MÉTRICAS POR TENANT
-- ==========================================

CREATE TABLE IF NOT EXISTS tenant_metrics (
    id BIGSERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    metric_date DATE NOT NULL DEFAULT CURRENT_DATE,
    total_requests INTEGER DEFAULT 0,
    successful_resolutions INTEGER DEFAULT 0,
    failed_resolutions INTEGER DEFAULT 0,
    avg_resolution_time_ms NUMERIC(10,2),
    unique_ips INTEGER DEFAULT 0,
    
    -- Constraint único por tenant y fecha
    UNIQUE (tenant_id, metric_date),
    
    -- Índices para reporting
    INDEX (tenant_id, metric_date DESC),
    INDEX (metric_date, total_requests DESC)
);

-- ==========================================
-- 🔍 VISTAS PARA CONSULTAS OPTIMIZADAS
-- ==========================================

-- Vista para productos activos por tenant (con stock)
CREATE OR REPLACE VIEW tenant_active_products AS
SELECT 
    p.client_id as tenant_id,
    p.id,
    p.name,
    p.price,
    p.stock,
    p.category,
    p.description,
    p.created_at
FROM products p
WHERE p.status = 'active' 
AND p.stock > 0
AND p.client_id IS NOT NULL;

-- Vista para pedidos recientes por tenant
CREATE OR REPLACE VIEW tenant_recent_orders AS
SELECT 
    o.client_id as tenant_id,
    o.id,
    o.phone,
    o.total_amount,
    o.status,
    o.created_at,
    COUNT(oi.id) as items_count
FROM orders o
LEFT JOIN order_items oi ON o.id = oi.order_id
WHERE o.created_at >= CURRENT_DATE - INTERVAL '30 days'
AND o.client_id IS NOT NULL
GROUP BY o.client_id, o.id, o.phone, o.total_amount, o.status, o.created_at;

-- Vista para estadísticas de sesiones activas por tenant
CREATE OR REPLACE VIEW tenant_active_sessions AS
SELECT 
    fs.tenant_id,
    COUNT(*) as total_sessions,
    COUNT(CASE WHEN fs.estado = 'activo' THEN 1 END) as active_sessions,
    COUNT(CASE WHEN fs.estado = 'esperando_respuesta' THEN 1 END) as waiting_sessions,
    MAX(fs.fecha_actualizacion) as last_activity
FROM flow_sesiones fs
WHERE fs.fecha_actualizacion >= CURRENT_DATE - INTERVAL '1 day'
AND fs.tenant_id IS NOT NULL
GROUP BY fs.tenant_id;

-- ==========================================
-- 🛡️ ROW LEVEL SECURITY (RLS) - OPCIONAL
-- ==========================================

-- Habilitar RLS en tabla products (si se requiere nivel adicional de seguridad)
-- ALTER TABLE products ENABLE ROW LEVEL SECURITY;

-- Política ejemplo para products (comentada - activar si se necesita)
-- CREATE POLICY tenant_products_policy ON products
-- FOR ALL TO app_user
-- USING (client_id = current_setting('app.current_tenant')::VARCHAR);

-- ==========================================
-- 📈 FUNCIONES DE UTILIDAD PARA MÉTRICAS
-- ==========================================

-- Función para actualizar métricas diarias por tenant
CREATE OR REPLACE FUNCTION update_tenant_daily_metrics(p_tenant_id VARCHAR, p_date DATE DEFAULT CURRENT_DATE)
RETURNS VOID AS $$
BEGIN
    INSERT INTO tenant_metrics (tenant_id, metric_date, total_requests, successful_resolutions, avg_resolution_time_ms)
    SELECT 
        p_tenant_id,
        p_date,
        COUNT(*),
        COUNT(CASE WHEN status = 'success' THEN 1 END),
        AVG(duration_ms)
    FROM tenant_resolution_audit
    WHERE tenant_id = p_tenant_id 
    AND DATE(timestamp) = p_date
    ON CONFLICT (tenant_id, metric_date)
    DO UPDATE SET
        total_requests = EXCLUDED.total_requests,
        successful_resolutions = EXCLUDED.successful_resolutions,
        avg_resolution_time_ms = EXCLUDED.avg_resolution_time_ms;
END;
$$ LANGUAGE plpgsql;

-- Función para limpiar auditoría antigua (retener 90 días)
CREATE OR REPLACE FUNCTION cleanup_old_audit_data()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM tenant_resolution_audit 
    WHERE timestamp < NOW() - INTERVAL '90 days';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ==========================================
-- 📋 COMENTARIOS Y DOCUMENTACIÓN
-- ==========================================

COMMENT ON TABLE tenant_resolution_audit IS 'Auditoría completa de resolución de tenants para seguridad y debugging';
COMMENT ON TABLE tenant_metrics IS 'Métricas agregadas por tenant para monitoring y reporting';

COMMENT ON INDEX idx_products_client_id_status IS 'Optimiza consultas de productos por tenant y estado';
COMMENT ON INDEX idx_orders_client_id_status IS 'Optimiza consultas de pedidos por tenant, estado y fecha';
COMMENT ON INDEX idx_flow_sesiones_tenant_telefono IS 'Crítico para bot WhatsApp - consultas por tenant y teléfono';

-- ==========================================
-- ✅ VERIFICACIÓN DE MIGRACIÓN
-- ==========================================

-- Verificar que todos los índices se crearon correctamente
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE indexname LIKE 'idx_%tenant%' 
   OR indexname LIKE 'idx_%client_id%'
ORDER BY tablename, indexname;

-- Verificar constraints
SELECT 
    table_name,
    constraint_name,
    constraint_type
FROM information_schema.table_constraints
WHERE constraint_name LIKE '%tenant%' 
   OR constraint_name LIKE '%client_id%'
ORDER BY table_name;

-- Script completado exitosamente
SELECT 'Migración de aislamiento multi-tenant completada exitosamente' as status;