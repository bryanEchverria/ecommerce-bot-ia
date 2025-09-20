-- 🤖 MEJORAS DE IA - ESQUEMA DE BASE DE DATOS
-- Tablas para entrenamiento y análisis de conversaciones

-- 1. Tabla de historial completo de mensajes
CREATE TABLE conversation_history (
    id SERIAL PRIMARY KEY,
    telefono VARCHAR(20) NOT NULL,
    tenant_id VARCHAR(100) NOT NULL,
    mensaje_usuario TEXT NOT NULL,
    respuesta_bot TEXT NOT NULL,
    intencion_detectada VARCHAR(100),
    productos_mencionados TEXT[], -- Array de productos detectados
    contexto_sesion TEXT, -- JSON con el contexto completo
    timestamp_mensaje TIMESTAMP DEFAULT NOW(),
    duracion_respuesta_ms INTEGER, -- Tiempo que tardó en responder
    satisfaccion_usuario INTEGER CHECK (satisfaccion_usuario BETWEEN 1 AND 5), -- Rating opcional
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2. Tabla de patrones de intenciones detectadas
CREATE TABLE intent_patterns (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    intencion VARCHAR(100) NOT NULL,
    patron_mensaje TEXT NOT NULL, -- El mensaje que activó esta intención
    productos_relacionados TEXT[], -- Productos que estaban en contexto
    frecuencia_uso INTEGER DEFAULT 1, -- Cuántas veces se ha usado este patrón
    efectividad DECIMAL(3,2) DEFAULT 0.0, -- % de éxito (0.0-1.0)
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 3. Tabla de análisis de productos más consultados
CREATE TABLE product_analytics (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    producto_id VARCHAR(100) NOT NULL,
    producto_nombre VARCHAR(255) NOT NULL,
    consultas_totales INTEGER DEFAULT 0,
    conversiones_compra INTEGER DEFAULT 0, -- Cuántos terminaron comprando
    abandonos INTEGER DEFAULT 0, -- Cuántos abandonaron después de consultar
    conversion_rate DECIMAL(5,2) DEFAULT 0.0, -- % de conversión
    fecha_analisis DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, producto_id, fecha_analisis)
);

-- 4. Tabla de contexto inteligente (memoria de conversaciones)
CREATE TABLE conversation_context (
    id SERIAL PRIMARY KEY,
    telefono VARCHAR(20) NOT NULL,
    tenant_id VARCHAR(100) NOT NULL,
    contexto_json TEXT NOT NULL, -- JSON con historial reciente, preferencias, etc.
    productos_interes TEXT[], -- Productos que ha mostrado interés
    ultima_actualizacion TIMESTAMP DEFAULT NOW(),
    expira_en TIMESTAMP, -- TTL para limpiar contextos antiguos
    UNIQUE(telefono, tenant_id)
);

-- 5. Tabla de feedback de calidad de respuestas
CREATE TABLE response_quality (
    id SERIAL PRIMARY KEY,
    conversation_history_id INTEGER REFERENCES conversation_history(id),
    telefono VARCHAR(20) NOT NULL,
    tenant_id VARCHAR(100) NOT NULL,
    fue_util BOOLEAN, -- true/false si la respuesta fue útil
    razon_feedback VARCHAR(500), -- Por qué fue útil o no
    sugerencia_mejora TEXT, -- Cómo mejorar la respuesta
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices para optimización de consultas
CREATE INDEX idx_conversation_history_telefono_tenant ON conversation_history(telefono, tenant_id);
CREATE INDEX idx_conversation_history_timestamp ON conversation_history(timestamp_mensaje DESC);
CREATE INDEX idx_conversation_history_intencion ON conversation_history(intencion_detectada);

CREATE INDEX idx_intent_patterns_tenant_intencion ON intent_patterns(tenant_id, intencion);
CREATE INDEX idx_intent_patterns_frecuencia ON intent_patterns(frecuencia_uso DESC);

CREATE INDEX idx_product_analytics_tenant_fecha ON product_analytics(tenant_id, fecha_analisis DESC);
CREATE INDEX idx_product_analytics_conversion ON product_analytics(conversion_rate DESC);

CREATE INDEX idx_conversation_context_telefono ON conversation_context(telefono, tenant_id);
CREATE INDEX idx_conversation_context_expira ON conversation_context(expira_en);

-- Función para limpiar contextos expirados automáticamente
CREATE OR REPLACE FUNCTION cleanup_expired_contexts()
RETURNS void AS $$
BEGIN
    DELETE FROM conversation_context 
    WHERE expira_en IS NOT NULL AND expira_en < NOW();
END;
$$ LANGUAGE plpgsql;

-- Función para actualizar estadísticas de productos automáticamente
CREATE OR REPLACE FUNCTION update_product_analytics()
RETURNS void AS $$
BEGIN
    -- Actualizar estadísticas diarias de productos consultados
    INSERT INTO product_analytics (tenant_id, producto_id, producto_nombre, consultas_totales, fecha_analisis)
    SELECT 
        ch.tenant_id,
        unnest(ch.productos_mencionados) as producto_id,
        'Producto ' || unnest(ch.productos_mencionados) as producto_nombre,
        COUNT(*) as consultas_totales,
        CURRENT_DATE
    FROM conversation_history ch
    WHERE DATE(ch.timestamp_mensaje) = CURRENT_DATE
    AND ch.productos_mencionados IS NOT NULL
    GROUP BY ch.tenant_id, unnest(ch.productos_mencionados)
    ON CONFLICT (tenant_id, producto_id, fecha_analisis)
    DO UPDATE SET 
        consultas_totales = EXCLUDED.consultas_totales,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- Comentarios explicativos
COMMENT ON TABLE conversation_history IS 'Historial completo de conversaciones para entrenamiento de IA';
COMMENT ON TABLE intent_patterns IS 'Patrones de intenciones detectadas para mejorar precisión';
COMMENT ON TABLE product_analytics IS 'Análisis de productos más consultados y conversiones';
COMMENT ON TABLE conversation_context IS 'Contexto inteligente para respuestas personalizadas';
COMMENT ON TABLE response_quality IS 'Feedback de calidad para mejora continua';