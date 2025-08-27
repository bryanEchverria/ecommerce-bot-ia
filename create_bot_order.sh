#!/bin/bash

ORDER_CODE="BOT-$(date +%s)"

echo "=== CREANDO ORDEN VIA WEBHOOK (Simulando Bot) ==="
echo "Código de orden: $ORDER_CODE"

curl -s -X POST "https://webhook.sintestesia.cl/api/tenant-orders/" \
  -H "Content-Type: application/json" \
  -d "{
    \"code\": \"$ORDER_CODE\",
    \"customer_name\": \"Cliente WhatsApp (+1234567890)\",
    \"total\": \"1299000\",
    \"status\": \"pending\"
  }" | jq .