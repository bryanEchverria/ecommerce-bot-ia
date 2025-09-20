# Multi-Tenant Testing - Production Subdominios

## 🏢 Cuentas de Prueba Creadas

### **ACME Corporation**
- **Subdominio:** `acme.sintestesia.cl`
- **Tenant ID:** `acme0001-2025-4001-8001-production01`
- **Slug:** `acme`
- **IP:** `31.97.162.56`

### **Bravo Solutions**  
- **Subdominio:** `bravo.sintestesia.cl`
- **Tenant ID:** `bravo001-2025-4001-8001-production01`
- **Slug:** `bravo`
- **IP:** `31.97.162.56`

## 🧪 Tests de Producción

### 1. Test con Subdominios Reales

```bash
# Test ACME Corporation
curl -H "Host: acme.sintestesia.cl" \
     -H "Content-Type: application/json" \
     https://api.sintestesia.cl/__debug/tenant

# Respuesta esperada:
# {
#   "tenant_id": "acme0001-2025-4001-8001-production01",
#   "resolved": true,
#   "message": "Tenant successfully resolved"
# }
```

```bash
# Test Bravo Solutions
curl -H "Host: bravo.sintestesia.cl" \
     -H "Content-Type: application/json" \
     https://api.sintestesia.cl/__debug/tenant

# Respuesta esperada:
# {
#   "tenant_id": "bravo001-2025-4001-8001-production01",
#   "resolved": true,
#   "message": "Tenant successfully resolved"
# }
```

### 2. Test con Headers Directos

```bash
# Test ACME con header directo
curl -H "X-Tenant-Id: acme0001-2025-4001-8001-production01" \
     -H "Content-Type: application/json" \
     https://api.sintestesia.cl/__debug/tenant
```

```bash
# Test Bravo con header directo
curl -H "X-Tenant-Id: bravo001-2025-4001-8001-production01" \
     -H "Content-Type: application/json" \
     https://api.sintestesia.cl/__debug/tenant
```

### 3. Test de Precedencia (Header > Subdomain)

```bash
# Header debe tomar precedencia sobre subdomain
curl -H "X-Tenant-Id: bravo001-2025-4001-8001-production01" \
     -H "Host: acme.sintestesia.cl" \
     -H "Content-Type: application/json" \
     https://api.sintestesia.cl/__debug/tenant

# Debe retornar tenant_id de BRAVO (del header), no de ACME (del host)
```

## 🌐 Tests Locales (Desarrollo)

### Simular Subdominios en Desarrollo

```bash
# Test local simulando acme.sintestesia.cl
curl -H "Host: acme.sintestesia.cl" \
     -H "Content-Type: application/json" \
     http://localhost:8002/__debug/tenant
```

```bash
# Test local simulando bravo.sintestesia.cl
curl -H "Host: bravo.sintestesia.cl" \
     -H "Content-Type: application/json" \
     http://localhost:8002/__debug/tenant
```

### Agregar a /etc/hosts (Opcional)

```bash
# Para testing local más realista, añadir a /etc/hosts:
echo "127.0.0.1 acme.sintestesia.cl" >> /etc/hosts
echo "127.0.0.1 bravo.sintestesia.cl" >> /etc/hosts

# Luego testear directamente:
curl http://acme.sintestesia.cl:8002/__debug/tenant
curl http://bravo.sintestesia.cl:8002/__debug/tenant
```

## 🚀 Tests de Integración Completa

### Test con Endpoints Reales de la API

```bash
# Test con endpoint de órdenes - ACME
curl -H "Host: acme.sintestesia.cl" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     https://api.sintestesia.cl/api/orders

# Test con endpoint de órdenes - Bravo  
curl -H "Host: bravo.sintestesia.cl" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     https://api.sintestesia.cl/api/orders
```

### Test con WhatsApp Bot

```bash
# Test webhook WhatsApp para ACME
curl -X POST \
     -H "Host: acme.sintestesia.cl" \
     -H "Content-Type: application/json" \
     -d '{"test": "webhook"}' \
     https://webhook.sintestesia.cl/whatsapp/webhook

# Test webhook WhatsApp para Bravo
curl -X POST \
     -H "Host: bravo.sintestesia.cl" \
     -H "Content-Type: application/json" \
     -d '{"test": "webhook"}' \
     https://webhook.sintestesia.cl/whatsapp/webhook
```

## 📊 Verificación de Datos

### Check Database State

```bash
# Verificar que las cuentas existen
docker exec ecommerce-postgres psql -U postgres -d ecommerce -c "
SELECT 
    slug,
    name,
    LEFT(id, 8) || '...' as tenant_id,
    created_at::date as created
FROM tenant_clients 
WHERE slug IN ('acme', 'bravo')
ORDER BY slug;
"
```

### Cache Performance

```bash
# Ver estadísticas de caché después de varios requests
curl https://api.sintestesia.cl/__debug/tenant/cache

# Limpiar caché si es necesario
curl -X POST https://api.sintestesia.cl/__debug/tenant/cache/clear
```

## 🔑 Casos de Uso Reales

### Frontend Multi-tenant

```javascript
// En tu frontend, configurar automáticamente según subdominio:
const subdomain = window.location.hostname.split('.')[0]; // 'acme' o 'bravo'
const apiHeaders = {
  'Host': window.location.hostname, // acme.sintestesia.cl
  'Content-Type': 'application/json'
};

fetch('/api/orders', { headers: apiHeaders });
```

### API Calls con Tenant Context

```python
# En tu código Python, el tenant se resuelve automáticamente
from app.middleware.tenant import get_tenant_id

@router.get("/dashboard")
async def get_dashboard():
    tenant_id = get_tenant_id()  # 'acme0001-...' o 'bravo001-...'
    
    # Filtrar datos por tenant automáticamente
    orders = db.query(Order).filter_by(tenant_id=tenant_id).all()
    return {"tenant": tenant_id, "orders": orders}
```

## 🚨 Troubleshooting

### Si los Tests Fallan

1. **Verificar DNS:**
   ```bash
   nslookup acme.sintestesia.cl
   nslookup bravo.sintestesia.cl
   ```

2. **Verificar Base de Datos:**
   ```bash
   docker exec ecommerce-postgres psql -U postgres -d ecommerce -c "
   SELECT * FROM tenant_clients WHERE slug IN ('acme', 'bravo');
   "
   ```

3. **Verificar Logs del Servidor:**
   ```bash
   docker logs -f ecommerce-backend | grep -i tenant
   ```

4. **Limpiar Caché:**
   ```bash
   curl -X POST http://localhost:8002/__debug/tenant/cache/clear
   ```

## ✅ Checklist de Validación

- [ ] ACME tenant creado con ID correcto
- [ ] Bravo tenant creado con ID correcto  
- [ ] Test con `acme.sintestesia.cl` funciona
- [ ] Test con `bravo.sintestesia.cl` funciona
- [ ] Headers tienen precedencia sobre subdominios
- [ ] Cache funciona correctamente
- [ ] Error 400 para subdominios inválidos
- [ ] Logs muestran resolución correcta

---

🎯 **Quick Tests:**

```bash
# Test rápido de ambos tenants:
curl -H "Host: acme.sintestesia.cl" http://localhost:8002/__debug/tenant
curl -H "Host: bravo.sintestesia.cl" http://localhost:8002/__debug/tenant
```

**¡Los subdominios de producción están listos para multi-tenancy!** 🏢✨