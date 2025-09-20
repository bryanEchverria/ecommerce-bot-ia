#!/bin/bash

WEBHOOK_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MWMxOWJmYy0zODI5LTRlODEtYTQ2OS1hZTFkMTkwZjhlZGYiLCJjbGllbnRfaWQiOiIyYWUxMzkzNy1jYmFhLTQ1YzUtYjdiYy05YzczNTg2NDgzZGUiLCJyb2xlIjoib3duZXIiLCJleHAiOjE3NTU3NTM4MTQsImlhdCI6MTc1NTc1MjkxNH0.qTYY8wrehKcvaLqEVhNKQ-XDTlxDJ0a-6hUt9TG4b2I"
ORDER_CODE="BOT-WEBHOOK-$(date +%s)"

echo "=== FLUJO COMPLETO: BOT → WEBHOOK → ORDEN ==="
echo "1. Conversación del bot completada ✅"
echo "2. Creando orden via webhook..."
echo "   Código: $ORDER_CODE"

# Crear orden via webhook (simula el bot creando la orden)
ORDEN_RESPONSE=$(curl -s -X POST "https://webhook.sintestesia.cl/api/tenant-orders/" \
  -H "Authorization: Bearer $WEBHOOK_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"code\": \"$ORDER_CODE\",
    \"customer_name\": \"Cliente WhatsApp (+1234567890)\",
    \"total\": \"1199.99\",
    \"status\": \"pending\"
  }")

echo "Resultado de creación de orden:"
echo "$ORDEN_RESPONSE" | jq .

echo ""
echo "3. Verificando que la orden aparece en el backoffice..."

# Verificar órdenes en el sistema
curl -s -X GET "https://api.sintestesia.cl/api/tenant-orders/" \
  -H "Authorization: Bearer $WEBHOOK_TOKEN" | jq .