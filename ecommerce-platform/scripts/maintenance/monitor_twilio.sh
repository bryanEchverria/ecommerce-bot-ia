#!/bin/bash
echo "🔍 Monitoreando mensajes de Twilio..."
echo "📱 Webhook: https://webhook.sintestesia.cl/twilio/webhook"
echo "📊 Logs en tiempo real:"
echo "----------------------------------------"

# Monitorear logs de nginx y backend
tail -f /var/log/nginx/webhook.sintestesia.cl.access.log &
docker logs -f ecommerce-backend | grep -i twilio &

wait