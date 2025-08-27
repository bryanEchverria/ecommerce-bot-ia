# 📱 Activar WhatsApp con Twilio

## 🔧 Configuración completada:
- ✅ Webhook funcionando: https://webhook.sintestesia.cl/twilio/webhook  
- ✅ Variables configuradas en contenedores
- ✅ Bot respondiendo correctamente
- ✅ SSL certificados válidos

## 📋 PASOS PARA ACTIVAR:

### 1. En Twilio Console:
1. Login: https://console.twilio.com
2. Ve a: **Develop > Messaging > Try it out > Send a WhatsApp message**
3. Configurar:
   ```
   Webhook URL: https://webhook.sintestesia.cl/twilio/webhook
   HTTP Method: POST
   Status callback URL: https://webhook.sintestesia.cl/twilio/status
   ```

### 2. En tu WhatsApp:
1. **Agregar contacto**: +1 415 523-8886
2. **Enviar mensaje**: `join worried-cat` (o el código que aparezca)
3. **Confirmación**: Deberías recibir "Joined worried-cat"

### 3. Probar el bot:
1. **Envía**: "hola" 
2. **Deberías recibir**: Respuesta de Green House 🌿
3. **Prueba**: "vaporizador" para ver producto

## 🔍 Monitorear mensajes:
```bash
/root/monitor_twilio.sh
```

## 📊 URLs importantes:
- **Webhook**: https://webhook.sintestesia.cl/twilio/webhook
- **Status**: https://webhook.sintestesia.cl/twilio/status  
- **Test**: https://webhook.sintestesia.cl/twilio/test
- **Backoffice**: https://app.sintestesia.cl
- **API**: https://api.sintestesia.cl

## ⚠️ Nota:
- Sandbox permite 1 número de prueba
- Para producción necesitas aprobación de Meta
- El bot funciona perfectamente, solo falta activar el sandbox