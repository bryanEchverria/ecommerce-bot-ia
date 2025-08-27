# WhatsApp Dual Provider Integration

## Resumen

Este proyecto ahora soporta dos integraciones de WhatsApp:
- **Twilio WhatsApp API** (existente)
- **Meta WhatsApp Cloud API** (nueva)

El sistema usa un patrón de adapters que permite cambiar entre proveedores fácilmente.

## Estructura del Código

```
whatsapp-bot-fastapi/
├── adapters/
│   ├── __init__.py
│   ├── base.py              # Interfaz WhatsAppAdapter
│   ├── twilio_adapter.py    # Implementación Twilio
│   └── meta_adapter.py      # Implementación Meta
├── api/
│   └── webhook_meta.py      # Webhook para Meta
├── services/
│   └── messaging.py         # Servicio unificado
├── settings.py              # Selector de proveedor
└── main.py                  # FastAPI app con ambos webhooks
```

## Configuración

### Variables de Entorno

```bash
# Selector de proveedor
WA_PROVIDER=twilio  # o "meta"

# Configuración Twilio (existente)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Configuración Meta WhatsApp Cloud API (nueva)
WHATSAPP_TOKEN=your-meta-whatsapp-business-token
WHATSAPP_VERIFY_TOKEN=your-meta-webhook-verify-token
WHATSAPP_PHONE_NUMBER_ID=your-meta-phone-number-id
GRAPH_API_VERSION=v21.0
```

### Selección de Proveedor

1. **Por variable de entorno**: Establece `WA_PROVIDER=twilio` o `WA_PROVIDER=meta`
2. **Por tenant (futuro)**: Descomenta la sección `TENANT_PROVIDER` en `settings.py`

## Endpoints

### Webhooks

1. **Webhook Twilio** (existente en backend): `/twilio/webhook`
2. **Webhook Meta** (nuevo): `/webhook/meta`
   - GET: Verificación del webhook (challenge)
   - POST: Recepción de mensajes

### Status y Testing

- **Status general**: `/status` - Muestra configuración de proveedores
- **Test Meta**: `/webhook/meta/test` - Verifica configuración Meta
- **Health check**: `/health` - Status de la aplicación

## Uso del Servicio de Mensajería

```python
from services.messaging import MessagingService, send_text, send_template

# Enviar texto (usa el proveedor configurado)
await MessagingService.send_text("+56912345678", "Hola mundo")

# O usando función de conveniencia
await send_text("+56912345678", "Hola mundo")

# Enviar template
components = {
    "body": [
        {"text": "Juan"},           # Parámetro 1
        {"text": "Producto X"}     # Parámetro 2
    ]
}
await send_template("+56912345678", "order_confirmation", "es", components)
```

## Configuración de Webhooks

### Meta WhatsApp Cloud API

1. **Verificación**: 
   ```
   GET /webhook/meta?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=CHALLENGE
   ```

2. **URL del Webhook**: `https://your-domain.com/webhook/meta`

3. **Token de Verificación**: Debe coincidir con `WHATSAPP_VERIFY_TOKEN`

### Twilio (Existente)

- **URL del Webhook**: `https://webhook.sintestesia.cl/twilio/webhook` (backend)
- No requiere cambios

## Fallback y Tolerancia a Fallos

El sistema incluye fallback automático:
- Si Meta falla, intenta usar Twilio
- Si Twilio falla, intenta usar Meta
- Logs detallados para debugging

## Templates

### Twilio
Usa ContentSid para templates aprobados. Configura:
```bash
TWILIO_WELCOME_TEMPLATE_SID=your-welcome-template-sid
TWILIO_ORDER_TEMPLATE_SID=your-order-template-sid
```

### Meta
Usa nombres de template y componentes estructurados:
```python
components = {
    "header": [{"text": "Header param"}],
    "body": [{"text": "Body param 1"}, {"text": "Body param 2"}],
    "buttons": [{"type": "quick_reply", "parameters": [{"text": "Button text"}]}]
}
```

## Testing

```bash
# Verificar status
curl http://localhost:9001/status

# Test webhook Meta
curl http://localhost:9001/webhook/meta/test

# Enviar mensaje test (formato JSON para webhook legacy)
curl -X POST http://localhost:9001/webhook \
  -H "Content-Type: application/json" \
  -d '{"telefono": "+56912345678", "mensaje": "Hola test"}'
```

## Logs

El sistema registra:
- Selección de proveedor
- Envío de mensajes (éxito/fallo)
- Fallbacks automáticos
- Errores de configuración

```bash
# Ver logs
docker-compose logs whatsapp-bot-fastapi -f
```

## Migración

Para migrar de Twilio a Meta:
1. Configura las variables de Meta
2. Cambia `WA_PROVIDER=meta`
3. Configura el webhook en Meta Business
4. Prueba con `/webhook/meta/test`

El código existente de Twilio permanece intacto y funcional.