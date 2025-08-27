# Postman Collections

Este directorio contiene las colecciones de Postman para probar el bot WhatsApp.

## 📋 Colecciones Disponibles

### Colección Principal
- `Bot_WhatsApp_Tests_Complete.json` - **Colección completa y actualizada**
  - Tests para todos los clientes (Green House, Demo Company, Mundo Canino, Test Store)
  - Pruebas específicas de vaporizador
  - Casos extremos
  - Flow de pagos

### Colecciones Legacy
- `WhatsApp_Bot_Postman_Collection_Updated.json` - Versión anterior
- `Bot_Tests_Simple.json` - Tests básicos

## 🎯 Prueba Clave

**Para demostrar que el bot es específico:**

1. **Importar:** `Bot_WhatsApp_Tests_Complete.json` en Postman
2. **Ejecutar:** "Green House Tests → 3. Comprar VAPO (Específico)"
3. **URL:** `POST http://localhost:8001/webhook`
4. **Body:**
```json
{
  "telefono": "+3456789012",
  "mensaje": "quiero un vapo"
}
```

## ✅ Respuesta Esperada

El bot debe encontrar específicamente: **PAX 3 Vaporizador Premium**

Esto demuestra que:
- ✅ Bot reconoce "vapo" como vaporizador
- ✅ OpenAI está funcionando
- ✅ Búsqueda es muy específica
- ✅ Multi-tenant funciona (Green House)