#!/bin/bash

PROD_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MWMxOWJmYy0zODI5LTRlODEtYTQ2OS1hZTFkMTkwZjhlZGYiLCJjbGllbnRfaWQiOiIyYWUxMzkzNy1jYmFhLTQ1YzUtYjdiYy05YzczNTg2NDgzZGUiLCJyb2xlIjoib3duZXIiLCJleHAiOjE3NTU3NTMzMzAsImlhdCI6MTc1NTc1MjQzMH0.hHDdBE_HfdzA3hu_H2U5NkXaPoKyUaPkbAyAiw2xliA"

echo "=== VERIFICANDO DATOS DE PRODUCCIÓN ==="
echo "Productos:"
curl -s -X GET "https://api.sintestesia.cl/api/products" \
  -H "Authorization: Bearer $PROD_TOKEN" | jq 'length'

echo "Órdenes:"
curl -s -X GET "https://api.sintestesia.cl/api/tenant-orders/" \
  -H "Authorization: Bearer $PROD_TOKEN" | jq 'length'