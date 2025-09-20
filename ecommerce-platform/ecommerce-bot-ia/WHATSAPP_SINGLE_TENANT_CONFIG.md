# WhatsApp Configuración Global (Single Tenant)

## Resumen

Se implementó un sistema de configuración global de WhatsApp que permite:

- ✅ **Mantener integraciones existentes**: Twilio y Meta siguen funcionando
- ✅ **Configuración global única**: Una sola configuración para toda la aplicación
- ✅ **Interfaz de usuario**: Backoffice para configurar y probar conexiones
- ✅ **Seguridad**: Tokens encriptados en base de datos
- ✅ **Fallback**: Variables de entorno como respaldo

## Arquitectura Single Tenant

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Frontend React    │    │   Backend FastAPI    │    │  WhatsApp Adapters  │
│                     │    │                      │    │                     │
│ ┌─────────────────┐ │    │ ┌──────────────────┐ │    │ ┌─────────────────┐ │
│ │ WhatsAppSettings│ │───▶│ │ whatsapp_settings│ │───▶│ │ TwilioAdapter   │ │
│ │   Component     │ │    │ │    Router        │ │    │ │ MetaAdapter     │ │
│ └─────────────────┘ │    │ └──────────────────┘ │    │ └─────────────────┘ │
│                     │    │                      │    │                     │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
           │                           │                           │
           │                           │                           │
           ▼                           ▼                           ▼
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│     Database        │    │   Encryption Service │    │  Settings Module    │
│                     │    │                      │    │                     │
│ whatsapp_settings   │    │ - Encrypt tokens     │    │ get_adapter()       │
│ - id=1 (único)      │    │ - Decrypt for use    │    │ - DB config first   │
│ - provider          │    │ - Use SECRET_KEY     │    │ - Env fallback      │
│ - encrypted tokens  │    │                      │    │                     │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
```

## Cambios vs Multi-Tenant

### Base de Datos

**Tabla:** `whatsapp_settings` (simplificada)

```sql
- id (Integer, PK, siempre = 1)          # Solo un registro
- provider (String: 'twilio' | 'meta')
- twilio_account_sid (String, nullable)
- twilio_auth_token (String, encrypted, nullable)
- twilio_from (String, nullable)
- meta_token (String, encrypted, nullable)
- meta_phone_number_id (String, nullable)
- meta_graph_api_version (String, default='v21.0')
- is_active (Boolean, default=True)
- created_at (DateTime)
- updated_at (DateTime)
```

### Backend API (Simplificado)

**Endpoints:** `/api/settings/whatsapp/`

- `POST /settings/whatsapp` - Crear/actualizar configuración global
- `GET /settings/whatsapp` - Obtener configuración (sin tokens)
- `POST /settings/whatsapp/test` - Probar envío
- `DELETE /settings/whatsapp` - Eliminar configuración
- `GET /settings/whatsapp/providers` - Info de proveedores

### Frontend UI (Sin tenant_id)

**Componente:** `WhatsAppSettings.tsx`

- No requiere autenticación por tenant
- Configuración global única
- Same UI experience, menos complejidad

### Lógica de Selección Simplificada

**Prioridad:**

1. **Base de datos global** (si existe y está activa)
2. **Variables de entorno globales** (fallback)

```python
# En get_adapter() - sin tenant_id
config = get_config_from_db()
if config:
    return create_adapter_with_config(config["provider"], config)

# Fallback a configuración global
return create_global_adapter()
```

## Flujo de Uso Simplificado

### 1. Configuración Inicial
```bash
# 1. Aplicar migración
cd backend/
alembic upgrade head

# 2. Reiniciar servicios
docker-compose restart
```

### 2. Configurar desde UI

1. **Acceder:** `/whatsapp-settings` en el backoffice
2. **Seleccionar:** Proveedor (Twilio/Meta)
3. **Configurar:** Credenciales específicas
4. **Activar:** Canal de WhatsApp
5. **Probar:** Envío de mensaje de prueba

### 3. Usar desde Bot

```python
# El bot automáticamente usa la configuración global
from services.messaging import send_text

await send_text("+56912345678", "Hola")
# ↑ Usará la configuración global de la DB o variables de entorno
```

## Ejemplos de Uso

### Configurar Proveedor Meta Global

```bash
curl -X POST "http://localhost:8000/api/settings/whatsapp" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "meta",
    "is_active": true,
    "meta_settings": {
      "token": "EAAG...",
      "phone_number_id": "123456789012345",
      "graph_api_version": "v21.0"
    }
  }'
```

### Probar Configuración

```bash
curl -X POST "http://localhost:8000/api/settings/whatsapp/test" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+56912345678",
    "message": "Prueba desde configuración global"
  }'
```

### Obtener Estado (sin tokens)

```bash
curl "http://localhost:8000/api/settings/whatsapp" \
  -H "Authorization: Bearer $TOKEN"

# Response:
{
  "id": 1,
  "provider": "meta",
  "is_active": true,
  "has_twilio_config": false,
  "has_meta_config": true,
  "meta_phone_number_id": "123456789012345",
  "meta_graph_api_version": "v21.0"
  # Nota: no se exponen tokens
}
```

## Ventajas del Single Tenant

### ✅ Simplicidad

- **Una sola configuración** por aplicación
- **No complejidad de tenant management**
- **Setup más rápido y sencillo**
- **Menos puntos de falla**

### ✅ Mantenimiento

- **Migración más simple**
- **Debugging más fácil**
- **Una sola fuente de verdad**
- **Configuración centralizada**

### ✅ Performance

- **Menos queries a DB**
- **No joins complejos**
- **Cache más eficiente**
- **Menos overhead**

## Variables de Entorno

### Globales (fallback)
```bash
WA_PROVIDER=twilio
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
WHATSAPP_TOKEN=EAAGxxxxx
WHATSAPP_PHONE_NUMBER_ID=123456789012345
GRAPH_API_VERSION=v21.0
```

### Para encriptación
```bash
SECRET_KEY=your-super-secret-jwt-key-change-in-production
```

## Migración desde Multi-Tenant

Si tenías multi-tenant y quieres migrar:

1. **Backup** configuraciones existentes
2. **Elegir configuración principal** (de tenant más usado)
3. **Aplicar migración** nueva
4. **Insertar configuración** elegida en nueva tabla
5. **Probar** funcionamiento

## Testing

### Curl Tests
```bash
# 1. Crear configuración
curl -X POST "http://localhost:8000/api/settings/whatsapp" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"provider":"twilio","is_active":true,"twilio_settings":{"account_sid":"AC...","auth_token":"token","from_number":"whatsapp:+14155238886"}}'

# 2. Obtener configuración
curl "http://localhost:8000/api/settings/whatsapp" \
  -H "Authorization: Bearer $TOKEN"

# 3. Probar envío
curl -X POST "http://localhost:8000/api/settings/whatsapp/test" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"+56912345678","message":"Test"}'
```

## Troubleshooting

### Problema: "Configuration not found"
- **Causa**: No hay configuración en DB ni env
- **Solución**: Configurar desde UI o establecer variables de entorno

### Problema: "Encryption error"
- **Causa**: SECRET_KEY cambió después de encriptar
- **Solución**: Re-configurar credenciales

### Logs Útiles
```bash
# Ver logs del backend
docker-compose logs backend -f | grep -i whatsapp

# Ver logs específicos
docker-compose logs whatsapp-bot-fastapi -f | grep -i adapter
```

## Próximos Pasos

- [ ] **Rate limiting** global
- [ ] **Métricas de envío** consolidadas
- [ ] **Templates globales** personalizables
- [ ] **Webhook configuration** única
- [ ] **Multi-región** opcional