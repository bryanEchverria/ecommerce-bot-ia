#!/bin/bash

# Token de autenticación 
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlN2JjYmM5My0yNzExLTQ2NWMtYmNmNi0xMDE4NWVkYjlkMzMiLCJjbGllbnRfaWQiOiJlMTg2NDZiYi1lZmQyLTQ2YWEtYjBjNC0yNGIwN2IzZDVlYzgiLCJyb2xlIjoib3duZXIiLCJleHAiOjE3NTU3NTEyMjgsImlhdCI6MTc1NTc1MDMyOH0.N62TjMPrtvZHbfcIpRTkIDd6qfx5zHf3TAN2PUuSW8s"

echo "=== CREANDO PRODUCTOS ==="

# Crear producto 1
curl -s -X POST "http://localhost:8000/api/products" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Smartphone Galaxy S23",
    "description": "Último modelo de smartphone Samsung con cámara de 200MP",
    "price": 899.99,
    "stock": 10,
    "category": "electronica",
    "status": "active",
    "image_url": "https://example.com/galaxy-s23.jpg"
  }' | jq .

# Crear producto 2
curl -s -X POST "http://localhost:8000/api/products" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop Gaming ROG",
    "description": "Laptop para gaming con RTX 4070 y procesador Intel i7",
    "price": 1599.99,
    "stock": 5,
    "category": "electronica",
    "status": "active",
    "image_url": "https://example.com/laptop-rog.jpg"
  }' | jq .

echo "=== VERIFICANDO PRODUCTOS ==="
curl -s -X GET "http://localhost:8000/api/products" \
  -H "Authorization: Bearer $TOKEN" | jq .

echo "=== PRODUCTOS DEL BOT ==="
curl -s -X GET "http://localhost:8000/api/bot/products/catalog" \
  -H "Authorization: Bearer $TOKEN" | jq .