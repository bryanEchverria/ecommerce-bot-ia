# Configuración Meta WhatsApp Cloud API

Esta guía explica cómo configurar completamente la integración con Meta WhatsApp Cloud API para el bot de e-commerce.

## 🚀 Configuración Inicial en Meta Business

### 1. Crear App en Meta Developers

1. Ve a [Meta Developers](https://developers.facebook.com/)
2. Crea una nueva aplicación de tipo "Business"
3. Agrega el producto "WhatsApp Business API"

### 2. Configurar WhatsApp Business API

1. En tu app, ve a WhatsApp > Getting Started
2. Copia los siguientes valores:
   - **Access Token**: Token temporal (24h) o permanente
   - **Phone Number ID**: ID del número de teléfono
   - **WhatsApp Business Account ID**: ID de la cuenta

### 3. Configurar Webhook

1. En WhatsApp > Configuration > Webhook
2. Configura:
   - **Callback URL**: `https://tu-dominio.com/webhook/meta`
   - **Verify Token**: Un token secreto que elijas
   - **Webhook fields**: Selecciona `messages`

## 🔧 Configuración del Servidor

### 1. Variables de Entorno

Crea/edita el archivo `.env` en `whatsapp-bot-fastapi/`:

```env
# Meta WhatsApp Configuration
WHATSAPP_TOKEN=tu_access_token_aqui
WHATSAPP_PHONE_NUMBER_ID=tu_phone_number_id_aqui
GRAPH_API_VERSION=v21.0
WHATSAPP_VERIFY_TOKEN=tu_verify_token_aqui
WHATSAPP_WEBHOOK_SECRET=tu_webhook_secret_opcional

# Provider Selection
WA_PROVIDER=meta

# Backend Integration
BACKEND_URL=http://localhost:8002
OPENAI_API_KEY=tu_openai_key_aqui

# Flow Payment Integration
FLOW_API_KEY=tu_flow_key_aqui
FLOW_SECRET_KEY=tu_flow_secret_aqui
FLOW_BASE_URL=https://sandbox.flow.cl/api
BASE_URL=https://tu-dominio.com
```

### 2. Configuración Automática

Ejecuta el script de configuración:

```bash
cd /root
python configure_meta_webhook.py
```

Este script:
- ✅ Verifica las variables de entorno
- 📱 Obtiene el WhatsApp Business Account ID
- 🔧 Configura el webhook automáticamente
- 🧪 Prueba la configuración

## 🐳 Docker Configuration

### 1. Actualizar docker-compose.yml

```yaml
services:
  whatsapp-bot:
    environment:
      # Meta WhatsApp
      WHATSAPP_TOKEN: ${WHATSAPP_TOKEN}
      WHATSAPP_PHONE_NUMBER_ID: ${WHATSAPP_PHONE_NUMBER_ID}
      GRAPH_API_VERSION: ${GRAPH_API_VERSION:-v21.0}
      WHATSAPP_VERIFY_TOKEN: ${WHATSAPP_VERIFY_TOKEN}
      WHATSAPP_WEBHOOK_SECRET: ${WHATSAPP_WEBHOOK_SECRET}
      WA_PROVIDER: meta
```

### 2. Ejecutar el servicio

```bash
cd ecommerce-bot-ia
docker-compose up whatsapp-bot -d
```

## 📋 Configuración desde el Backend

También puedes configurar Meta WhatsApp desde el panel de administración:

### 1. Acceder al Panel

1. Ve a `https://tu-dominio.com/admin`
2. Inicia sesión con credenciales de administrador
3. Ve a "Configuración WhatsApp"

### 2. Configurar Meta

1. Selecciona "Meta WhatsApp Cloud API" como proveedor
2. Completa los campos:
   - **Access Token**: Tu token de Meta
   - **Phone Number ID**: ID del número
   - **Graph API Version**: v21.0 (recomendado)
3. Guarda la configuración

## 🧪 Pruebas

### 1. Verificar Estado

```bash
curl https://tu-dominio.com/webhook/meta/test
```

### 2. Probar Webhook

```bash
curl -X GET "https://tu-dominio.com/webhook/meta?hub.mode=subscribe&hub.verify_token=tu_verify_token&hub.challenge=test123"
```

Debe devolver `test123`.

### 3. Enviar Mensaje de Prueba

Envía un mensaje WhatsApp al número configurado y verifica los logs:

```bash
docker logs ecommerce-whatsapp-bot -f
```

## 🔐 Seguridad

### 1. Verificación de Firma (Recomendado)

Configura `WHATSAPP_WEBHOOK_SECRET` para verificar que los webhooks provienen de Meta:

1. En Meta Developers > WhatsApp > Configuration
2. Configura el "Webhook Secret"
3. Añade la variable de entorno `WHATSAPP_WEBHOOK_SECRET`

### 2. HTTPS Obligatorio

Meta requiere que tu webhook use HTTPS. Configura SSL/TLS en tu servidor.

## 🚨 Troubleshooting

### Error: "Invalid signature"
- Verifica que `WHATSAPP_WEBHOOK_SECRET` coincida con Meta
- Asegúrate de que el webhook esté configurado correctamente

### Error: "Verification token mismatch"
- Verifica que `WHATSAPP_VERIFY_TOKEN` coincida exactamente
- Revisa la configuración en Meta Developers

### Error: "Invalid phone number format"
- Los números deben estar en formato E.164 (+56912345678)
- El sistema normaliza automáticamente los números

### Mensajes no se reciben
1. Verifica que el webhook esté configurado en Meta
2. Revisa los logs del contenedor
3. Confirma que el puerto 9001 esté accesible
4. Verifica la configuración HTTPS

## 📞 Soporte

Para problemas específicos:

1. **Logs del sistema**: `docker logs ecommerce-whatsapp-bot`
2. **Estado del webhook**: `/webhook/meta/test`
3. **Configuración**: `/status`

## 🔄 Migración desde Twilio

Si vienes desde Twilio:

1. Cambia `WA_PROVIDER=meta` en `.env`
2. Configura las variables de Meta
3. Ejecuta `configure_meta_webhook.py`
4. Reinicia los servicios

El sistema cambiará automáticamente al proveedor Meta sin perder funcionalidad.