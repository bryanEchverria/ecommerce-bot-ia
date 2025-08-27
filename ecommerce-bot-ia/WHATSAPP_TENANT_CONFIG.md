# WhatsApp Configuración por Tenant

## Resumen

Se implementó un sistema completo de configuración de WhatsApp por tenant que permite:

- ✅ **Mantener integraciones existentes**: Twilio y Meta siguen funcionando
- ✅ **Configuración dinámica por tenant**: Cada tenant puede tener su propio proveedor y credenciales
- ✅ **Interfaz de usuario**: Backoffice para configurar y probar conexiones
- ✅ **Seguridad**: Tokens encriptados en base de datos
- ✅ **Fallback**: Variables de entorno como respaldo

## Arquitectura

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
│ whatsapp_channel_   │    │ - Encrypt tokens     │    │ get_adapter()       │
│ settings            │    │ - Decrypt for use    │    │ - DB config first   │
│ - tenant_id (PK)    │    │ - Use SECRET_KEY     │    │ - Env fallback      │
│ - provider          │    │                      │    │                     │
│ - encrypted tokens  │    │                      │    │                     │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
```

## Componentes Implementados

### 1. Base de Datos

**Tabla:** `whatsapp_channel_settings`

```sql
- id (String, PK)
- tenant_id (String, Unique) 
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

### 2. Backend API

**Endpoints:** `/api/settings/whatsapp/`

- `POST /settings/whatsapp` - Crear/actualizar configuración
- `GET /settings/whatsapp/{tenant_id}` - Obtener configuración (sin tokens)
- `POST /settings/whatsapp/{tenant_id}/test` - Probar envío
- `DELETE /settings/whatsapp/{tenant_id}` - Eliminar configuración
- `GET /settings/whatsapp/{tenant_id}/providers` - Info de proveedores

### 3. Frontend UI

**Componente:** `WhatsAppSettings.tsx`

- Selector de proveedor (Twilio / Meta)
- Formularios específicos por proveedor
- Activación/desactivación del canal
- Prueba de envío de mensajes
- Estado actual de configuración

### 4. Seguridad

**Servicio de Encriptación:** `encryption_service.py`

- Usa `cryptography.fernet` con `PBKDF2HMAC`
- Deriva clave desde `SECRET_KEY`
- Encripta `twilio_auth_token` y `meta_token`
- Nunca expone tokens en respuestas GET

### 5. Lógica de Selección

**Prioridad de configuración:**

1. **Base de datos del tenant** (si existe y está activa)
2. **Variables de entorno globales** (fallback)

```python
# En get_adapter(tenant_id)
if tenant_id:
    config = get_tenant_config_from_db(tenant_id)
    if config:
        return create_adapter_with_config(config["provider"], config)

# Fallback a configuración global
return create_global_adapter()
```

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

### Nuevas (para encriptación)
```bash
SECRET_KEY=your-super-secret-jwt-key-change-in-production
```

## Flujo de Uso

### 1. Configuración Inicial
```bash
# 1. Aplicar migración
cd backend/
alembic upgrade head

# 2. Instalar dependencia de encriptación
pip install cryptography

# 3. Reiniciar servicios
docker-compose restart
```

### 2. Configurar Tenant desde UI

1. **Acceder:** `/whatsapp-settings` en el backoffice
2. **Seleccionar:** Proveedor (Twilio/Meta)
3. **Configurar:** Credenciales específicas
4. **Activar:** Canal de WhatsApp
5. **Probar:** Envío de mensaje de prueba

### 3. Usar desde Bot

```python
# El bot automáticamente usa la configuración del tenant
from services.messaging import send_text

await send_text("+56912345678", "Hola", tenant_id="mundo_canino")
# ↑ Usará la configuración específica de "mundo_canino"
```

## Ejemplos de Uso

### Configurar Tenant "Mundo Canino" con Meta

```bash
curl -X POST "http://localhost:8000/api/settings/whatsapp" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "mundo_canino",
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
curl -X POST "http://localhost:8000/api/settings/whatsapp/mundo_canino/test" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+56912345678",
    "message": "Prueba desde Mundo Canino"
  }'
```

### Obtener Estado (sin tokens)

```bash
curl "http://localhost:8000/api/settings/whatsapp/mundo_canino" \
  -H "Authorization: Bearer $TOKEN"

# Response:
{
  "id": "uuid-xxx",
  "tenant_id": "mundo_canino",
  "provider": "meta",
  "is_active": true,
  "has_twilio_config": false,
  "has_meta_config": true,
  "meta_phone_number_id": "123456789012345",
  "meta_graph_api_version": "v21.0"
  # Nota: no se exponen tokens
}
```

## Seguridad y Consideraciones

### ✅ Buenas Prácticas Implementadas

- **Tokens encriptados** en base de datos
- **No exposición** de tokens en APIs GET
- **Validación** de permisos por tenant
- **Fallback robusto** a configuración global
- **Logs detallados** para debugging

### ⚠️ Consideraciones de Producción

1. **Rotación de SECRET_KEY**: Cambiar en producción
2. **Backup de configuraciones**: Antes de migraciones
3. **Monitoreo**: Logs de envío por tenant
4. **Rate limiting**: Por tenant/proveedor
5. **Salt único**: Para cada instalación

## Testing

### Backend
```bash
# Test endpoints
python -m pytest tests/test_whatsapp_settings.py

# Test adapters
python -m pytest tests/test_adapters.py
```

### Frontend
```bash
# Component tests
npm test -- --testPathPattern=WhatsAppSettings

# Integration tests
npm run test:integration
```

### Manual Testing
```bash
# 1. Create tenant config via UI
# 2. Send message from bot
# 3. Verify correct adapter used
# 4. Test fallback with disabled config
```

## Migración desde Sistema Anterior

El sistema es **100% retrocompatible**:

1. **Código existente** sigue funcionando sin cambios
2. **Variables de entorno** siguen siendo el fallback
3. **Nuevas configuraciones** se almacenan en DB
4. **Sin downtime** durante migración

## Troubleshooting

### Problema: "No adapter found"
- **Causa**: Falta configuración para tenant
- **Solución**: Agregar config en UI o usar variables de entorno

### Problema: "Encryption error" 
- **Causa**: SECRET_KEY cambiado después de encriptar
- **Solución**: Re-configurar credenciales o restaurar SECRET_KEY

### Problema: "Token invalid"
- **Causa**: Credenciales incorrectas o expiradas
- **Solución**: Actualizar tokens en UI

### Logs Útiles
```bash
# Ver logs del backend
docker-compose logs backend -f | grep -i whatsapp

# Ver logs de adapters
docker-compose logs whatsapp-bot-fastapi -f | grep -i adapter
```

## Próximos Pasos

- [ ] **Rate limiting** por tenant
- [ ] **Métricas de envío** por proveedor
- [ ] **Templates personalizados** por tenant
- [ ] **Webhook configuration** por tenant
- [ ] **Multi-región** para Meta WhatsApp