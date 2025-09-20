#!/bin/bash

PROD_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MWMxOWJmYy0zODI5LTRlODEtYTQ2OS1hZTFkMTkwZjhlZGYiLCJjbGllbnRfaWQiOiIyYWUxMzkzNy1jYmFhLTQ1YzUtYjdiYy05YzczNTg2NDgzZGUiLCJyb2xlIjoib3duZXIiLCJleHAiOjE3NTU3NTMzMzAsImlhdCI6MTc1NTc1MjQzMH0.hHDdBE_HfdzA3hu_H2U5NkXaPoKyUaPkbAyAiw2xliA"

echo "=== CREANDO PRODUCTOS EN PRODUCCIÓN ==="

curl -s -X POST "https://api.sintestesia.cl/api/products" \
  -H "Authorization: Bearer $PROD_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "iPhone 15 Pro",
    "description": "Último modelo de iPhone con titanio y chip A17 Pro",
    "price": 1199.99,
    "stock": 15,
    "category": "smartphones", 
    "status": "active",
    "image_url": "https://via.placeholder.com/300x300/007FFF/FFFFFF?text=iPhone+15+Pro"
  }' | jq .

curl -s -X POST "https://api.sintestesia.cl/api/products" \
  -H "Authorization: Bearer $PROD_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MacBook Air M3",
    "description": "Nueva MacBook Air con chip M3",
    "price": 1099.99,
    "stock": 8,
    "category": "laptops",
    "status": "active",
    "image_url": "https://via.placeholder.com/300x300/808080/FFFFFF?text=MacBook+Air+M3"
  }' | jq .

echo "=== CREANDO ORDEN DE PRUEBA ==="

curl -s -X POST "https://api.sintestesia.cl/api/tenant-orders/" \
  -H "Authorization: Bearer $PROD_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "DEMO-001",
    "customer_name": "Cliente Demo",
    "total": "1199.99",
    "status": "pending"
  }' | jq .