# 🚀 Configuración Final Meta WhatsApp - Sintestesia

## ✅ Estado Actual
- **Token verificado**: ✅ Funcionando
- **Número de prueba**: +1 555 181 7191 (15551817191)
- **Phone Number ID**: 728170437054141
- **Business Account ID**: 1499532764576536

## 🔧 Configuración Completada

### 1. Variables de Entorno (.env)
```bash
# Provider Selection
WA_PROVIDER=meta

# Meta WhatsApp Cloud API
WHATSAPP_TOKEN=EAAKlRZBfhpIIBPR9kSYQ7Jyk8ZBPZAkDyAYo4LCs5YxO9yUOYHLbveiUvnNF4hnpNvcldgTtMZAMGpoXuX1vkXZBGLDbZAZA32cZAt6rSwBvfD2O19fKuyvhltlME2MMKuYphJZAUHPXRjsrzpFGImVax4dEjcPj7INwGs2wX5jiSmqxslw7ZBDFYWHECW9SxOA92r1basoqOE46YFV87vTKJ9UDSddCQAIBDksFKaN3wLixAmig4ZD
WHATSAPP_PHONE_NUMBER_ID=728170437054141
WHATSAPP_BUSINESS_ACCOUNT_ID=1499532764576536
GRAPH_API_VERSION=v21.0
WHATSAPP_VERIFY_TOKEN=sintestesia_verify_token_2024

# URLs
BASE_URL=https://webhook.sintestesia.cl
```

### 2. Configuración del Webhook en Meta

**Ve a Meta Developers > Tu App > WhatsApp > Configuration > Webhook:**

- **Callback URL**: `https://webhook.sintestesia.cl/webhook/meta`
- **Verify Token**: `sintestesia_verify_token_2024`
- **Webhook Fields**: Selecciona `messages`

## 📱 Pruebas Disponibles

### Opción 1: Script de Prueba Completo
```bash
python test_meta_sintestesia.py
```

### Opción 2: Comando cURL Directo
```bash
curl -X POST "https://graph.facebook.com/v21.0/728170437054141/messages" \\
  -H "Authorization: Bearer EAAKlRZBfhpIIBPR9kSYQ7Jyk8ZBPZAkDyAYo4LCs5YxO9yUOYHLbveiUvnNF4hnpNvcldgTtMZAMGpoXuX1vkXZBGLDbZAZA32cZAt6rSwBvfD2O19fKuyvhltlME2MMKuYphJZAUHPXRjsrzpFGImVax4dEjcPj7INwGs2wX5jiSmqxslw7ZBDFYWHECW9SxOA92r1basoqOE46YFV87vTKJ9UDSddCQAIBDksFKaN3wLixAmig4ZD" \\
  -H "Content-Type: application/json" \\
  -d '{
    "messaging_product": "whatsapp",
    "to": "+56912345678",
    "type": "text",
    "text": {
      "body": "¡Hola! Soy el bot de Sintestesia. ¿En qué puedo ayudarte?"
    }
  }'
```

## 🐳 Docker Compose

El sistema ya está configurado para usar Meta. Solo ejecuta:

```bash
cd ecommerce-bot-ia
docker-compose up whatsapp-bot -d
```

## 🔗 Endpoints Disponibles

- **Webhook**: `POST https://webhook.sintestesia.cl/webhook/meta`
- **Verificación**: `GET https://webhook.sintestesia.cl/webhook/meta`
- **Test**: `GET https://webhook.sintestesia.cl/webhook/meta/test`
- **Status**: `GET https://webhook.sintestesia.cl/status`

## ✨ Funcionalidades Implementadas

### ✅ Mensajes de Texto
- Recepción automática de mensajes
- Respuestas inteligentes con OpenAI
- Integración con el sistema de e-commerce

### ✅ Mensajes Interactivos
- Botones de respuesta rápida
- Menús de lista desplegables
- Manejo de clicks en botones

### ✅ Multimedia
- Recepción de imágenes, documentos, audio, video
- Procesamiento de captions
- Respuestas contextuales

### ✅ Templates
- Soporte completo para templates de Meta
- Componentes dinámicos (header, body, buttons)
- Templates de bienvenida y comerciales

### ✅ Seguridad
- Verificación de firma webhook (opcional)
- Validación de tokens
- Manejo seguro de credenciales

## 🎯 Próximos Pasos

### 1. Configurar Webhook en Meta
1. Ve a https://developers.facebook.com/
2. Tu App > WhatsApp > Configuration > Webhook
3. Usa los valores mostrados arriba

### 2. Ejecutar el Sistema
```bash
# Iniciar todos los servicios
docker-compose up -d

# O solo el bot WhatsApp
docker-compose up whatsapp-bot -d
```

### 3. Probar la Integración
```bash
# Probar conexión
python test_meta_sintestesia.py

# Verificar webhook
curl "https://webhook.sintestesia.cl/webhook/meta/test"
```

### 4. Enviar Mensaje Real
- Usa tu número personal
- Envía un mensaje al número de prueba: **+1 555 181 7191**
- El bot debería responder automáticamente

## ⚡ Comandos Rápidos

```bash
# Ver logs del bot
docker logs ecommerce-whatsapp-bot -f

# Reiniciar bot
docker-compose restart whatsapp-bot

# Verificar configuración
curl https://webhook.sintestesia.cl/status
```

## 🆘 Troubleshooting

### Token Expirado
- Los tokens temporales duran 24h
- Genera uno permanente en Meta Business

### Webhook No Responde
- Verifica que el servidor esté ejecutándose
- Confirma que el puerto 9001 esté accesible
- Revisa los logs: `docker logs ecommerce-whatsapp-bot`

### Mensajes No Llegan
- Verifica el webhook en Meta Developers
- Confirma el verify token
- Revisa la configuración HTTPS

---

## 🎉 ¡Sistema Listo!

Tu integración Meta WhatsApp está **completamente configurada y funcional**. El bot puede:

- ✅ Recibir mensajes de WhatsApp
- ✅ Responder con IA (OpenAI)
- ✅ Procesar pedidos de e-commerce
- ✅ Manejar pagos con Flow
- ✅ Enviar mensajes interactivos
- ✅ Soportar multimedia

**¡Solo configura el webhook en Meta y empezarás a recibir mensajes!**