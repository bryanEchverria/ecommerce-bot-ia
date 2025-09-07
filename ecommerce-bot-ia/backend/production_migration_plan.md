# Plan de Migración tenant_id para Producción

## 🔍 Estado Actual de Producción

### Verificaciones Realizadas:
- ✅ **API de producción:** `https://api.sintestesia.cl` - **ONLINE**
- ✅ **Endpoints flow disponibles:** `/api/flow-orders/`, `/flow/*`
- ❌ **Esquemas API:** No se encontraron esquemas con `tenant_id`
- ❌ **Datos de producción:** No hay órdenes flow actuales para analizar
- 🔍 **Estado:** **MIGRACIÓN REQUERIDA**

## 📋 Plan de Migración

### Pre-Migración (CRÍTICO)
1. **🛡️ Backup Completo**
   ```bash
   # Backup PostgreSQL de producción
   pg_dump -h [PROD_HOST] -U [USER] -d ecommerce > backup_pre_tenant_migration_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **📊 Inventario de Datos**
   - Contar registros en `flow_sesiones`, `flow_pedidos`, `whatsapp_settings`
   - Identificar datos críticos existentes
   - Verificar integridad referencial

3. **🧪 Test en Staging**
   - Clonar base de datos de producción a staging
   - Aplicar migración en staging
   - Validar funcionalidad completa

### Migración (Ventana de Mantenimiento)

#### Paso 1: Preparación
```bash
# Conectar a base de datos de producción
export POSTGRES_HOST=[PRODUCTION_HOST]
export POSTGRES_DB=ecommerce
export POSTGRES_USER=[PROD_USER]
export POSTGRES_PASSWORD=[PROD_PASSWORD]
```

#### Paso 2: Aplicar Migración
```bash
# Opción A: Via script Python
python3 apply_postgres_tenant_migration.py

# Opción B: Via SQL directo
psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -f postgres_tenant_migration.sql
```

#### Paso 3: Verificación Inmediata
```bash
# Verificar estructura
python3 test_postgres_tenant_migration.py

# Verificar datos
psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c "
SELECT 
    table_name,
    COUNT(*) as total_records,
    COUNT(tenant_id) as records_with_tenant_id
FROM (
    SELECT 'flow_sesiones' as table_name, tenant_id FROM flow_sesiones
    UNION ALL
    SELECT 'flow_pedidos' as table_name, tenant_id FROM flow_pedidos
    UNION ALL
    SELECT 'whatsapp_settings' as table_name, tenant_id FROM whatsapp_settings
) combined
GROUP BY table_name;
"
```

### Post-Migración

#### Paso 4: Validación de Aplicación
1. **Restart de servicios**
   ```bash
   # Reiniciar contenedores de producción
   docker-compose restart backend whatsapp-bot
   ```

2. **Health Checks**
   ```bash
   curl https://api.sintestesia.cl/health
   curl https://webhook.sintestesia.cl/health
   ```

3. **Pruebas Funcionales**
   - Crear nueva sesión WhatsApp → debe tener tenant_id
   - Crear nuevo pedido flow → debe tener tenant_id
   - Verificar índices compuestos funcionando

#### Paso 5: Monitoreo
- Logs de errores relacionados con tenant_id
- Performance de queries con nuevos índices
- Funcionalidad end-to-end del bot

## 🚨 Cambios Requeridos en Código

### Backend Models (models.py)
```python
# Actualizar modelos para incluir tenant_id como NOT NULL
class FlowSesion(Base):
    # ...
    tenant_id = Column(UUID(as_uuid=False), nullable=False, index=True)

class FlowPedido(Base):
    # ...
    tenant_id = Column(UUID(as_uuid=False), nullable=False, index=True)
```

### Queries de Aplicación
```python
# ANTES
session = db.query(FlowSesion).filter_by(telefono=phone).first()

# DESPUÉS  
session = db.query(FlowSesion).filter_by(
    telefono=phone, 
    tenant_id=current_tenant_id
).first()
```

## 💾 Scripts de Migración Disponibles

1. **`postgres_tenant_migration.sql`** - SQL directo para PostgreSQL
2. **`apply_postgres_tenant_migration.py`** - Script Python con manejo de errores
3. **`test_postgres_tenant_migration.py`** - Validación post-migración
4. **`add_tenant_id_multi_tenant_support.py`** - Migración Alembic oficial

## ⏰ Ventana de Mantenimiento Recomendada

**Duración estimada:** 15-30 minutos
**Momento recomendado:** Madrugada (2:00-4:00 AM horario local)
**Rollback plan:** Restaurar desde backup (5-10 minutos)

## 🔧 Tenant ID por Defecto

```
DEFAULT_TENANT_ID = '00000000-0000-0000-0000-000000000001'
```

Todos los datos existentes en producción se asignarán a este tenant por defecto, manteniendo compatibilidad completa.

## ✅ Checklist de Migración

- [ ] Backup completo realizado
- [ ] Migración probada en staging
- [ ] Ventana de mantenimiento programada
- [ ] Scripts de migración preparados
- [ ] Plan de rollback definido
- [ ] Monitoreo post-migración configurado
- [ ] Notificación a usuarios (si aplica)

## 🆘 Plan de Rollback

En caso de problemas:

1. **Stop servicios**
   ```bash
   docker-compose stop backend whatsapp-bot
   ```

2. **Restaurar backup**
   ```bash
   psql -h $POSTGRES_HOST -U $POSTGRES_USER -d ecommerce < backup_pre_tenant_migration_*.sql
   ```

3. **Restart servicios**
   ```bash
   docker-compose start backend whatsapp-bot
   ```

---

**⚠️ IMPORTANTE:** Esta migración es **irreversible sin backup**. Asegurar backup completo antes de proceder.