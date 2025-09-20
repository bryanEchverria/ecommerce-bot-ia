# 🌐 ARQUITECTURA WEBHOOKS MULTI-TENANT
## Sistema Dinámico Escalable para Múltiples Clientes

### 📅 Última actualización: 2025-09-19
### 🏷️ Versión: v4.0 - Sistema Completamente Dinámico

---

## 🏗️ ARQUITECTURA GENERAL

El sistema implementa **tres métodos de webhook** para máxima flexibilidad:

### 1. **Webhooks por Subdominio (Twilio - RECOMENDADO)**
```
https://{cliente}.sintestesia.cl/bot/twilio/webhook
```

### 2. **Webhooks por Slug Dinámico (API Interna)**
```
http://localhost:9001/webhook/{slug}
```

### 3. **Webhook Legacy (Compatibilidad)**
```
http://localhost:9001/webhook
```

---

## 🔧 CONFIGURACIÓN POR CLIENTE

### **Cliente ACME Cannabis**
- **Subdominio Twilio:** `https://acme.sintestesia.cl/bot/twilio/webhook`
- **Slug Interno:** `http://localhost:9001/webhook/acme`
- **Tenant ID:** `acme-cannabis-2024`
- **Productos:** Cannabis, flores, aceites, semillas

### **Cliente Bravo Gaming**
- **Subdominio Twilio:** `https://bravo.sintestesia.cl/bot/twilio/webhook`
- **Slug Interno:** `http://localhost:9001/webhook/bravo`
- **Tenant ID:** `bravo-gaming-2024`
- **Productos:** Consolas, videojuegos, accesorios gaming

### **Cliente Mundo Canino**
- **Subdominio Twilio:** `https://mundo-canino.sintestesia.cl/bot/twilio/webhook`
- **Slug Interno:** `http://localhost:9001/webhook/mundo-canino`
- **Tenant ID:** `mundo-canino-2024`
- **Productos:** Comida para perros, juguetes, accesorios mascotas

### **Cualquier Cliente Nuevo**
- **Subdominio Twilio:** `https://{slug}.sintestesia.cl/bot/twilio/webhook`
- **Slug Interno:** `http://localhost:9001/webhook/{slug}`
- **Tenant ID:** `{slug}-{año}` (automático)
- **Productos:** Según configuración en base de datos

---

## 🤖 DETECCIÓN AUTOMÁTICA DE TENANTS

### **Por Subdominio (Twilio)**
```python
# Extrae "acme" de "acme.sintestesia.cl"
subdomain = host.split('.')[0]
tenant = db.query(TenantClient).filter(TenantClient.slug == subdomain).first()
```

### **Por Slug (API Interna)**
```python
# Busca tenant por slug directo
tenant = get_tenant_from_slug(db, slug)
```

### **Métodos de Búsqueda (En orden):**
1. **Slug exacto** en `tenant_clients.slug`
2. **Patrón en ID** como `{slug}-{año}`
3. **Nombre similar** (fuzzy matching)

---

## 📊 ENDPOINTS DISPONIBLES

### **1. Listar Tenants Disponibles**
```bash
GET http://localhost:9001/tenants
```

**Respuesta:**
```json
{
  "status": "success",
  "total_tenants": 5,
  "tenants": [
    {
      "id": "acme-cannabis-2024",
      "name": "ACME Cannabis Store",
      "slug": "acme",
      "webhook_url": "/webhook/acme",
      "full_webhook_url": "http://localhost:9001/webhook/acme",
      "status": "active"
    }
  ]
}
```

### **2. Webhook Dinámico por Slug**
```bash
POST http://localhost:9001/webhook/{slug}
Content-Type: application/json

{
  "telefono": "+56999999999",
  "mensaje": "hola"
}
```

### **3. Webhook Twilio Multi-tenant**
```bash
POST https://{slug}.sintestesia.cl/bot/twilio/webhook
Content-Type: application/x-www-form-urlencoded

From=whatsapp:+56999999999&Body=hola&MessageSid=...
```

---

## 🔄 FLUJO DE PROCESAMIENTO

### **1. Recepción del Mensaje**
```
Cliente WhatsApp → Twilio → acme.sintestesia.cl/bot/twilio/webhook
```

### **2. Detección del Tenant**
```python
host = "acme.sintestesia.cl"
subdomain = "acme"  # Extraído automáticamente
tenant = buscar_tenant_por_slug("acme")
```

### **3. Procesamiento Específico**
```python
tenant_id = "acme-cannabis-2024"
productos = obtener_productos_tenant(tenant_id)
respuesta = procesar_con_ia(mensaje, productos, tenant_id)
```

### **4. Respuesta Personalizada**
```python
enviar_respuesta_twilio(respuesta, configuracion_tenant)
```

---

## 🗄️ ESTRUCTURA DE BASE DE DATOS

### **Tabla: tenant_clients**
```sql
CREATE TABLE tenant_clients (
    id VARCHAR PRIMARY KEY,           -- "acme-cannabis-2024"
    name VARCHAR NOT NULL,            -- "ACME Cannabis Store"
    slug VARCHAR UNIQUE NOT NULL,     -- "acme"
    created_at TIMESTAMP
);
```

### **Tabla: twilio_accounts**
```sql
CREATE TABLE twilio_accounts (
    id VARCHAR PRIMARY KEY,
    tenant_id VARCHAR REFERENCES tenant_clients(id),
    account_sid VARCHAR NOT NULL,
    auth_token_enc TEXT NOT NULL,     -- Token encriptado
    from_number VARCHAR,
    status VARCHAR DEFAULT 'active'
);
```

### **Tabla: products**
```sql
CREATE TABLE products (
    id VARCHAR PRIMARY KEY,
    name VARCHAR,
    client_id VARCHAR,                -- tenant_id
    price FLOAT,
    stock INTEGER,
    status VARCHAR                    -- 'Active'
);
```

---

## 🚀 AGREGAR NUEVO CLIENTE

### **1. Crear Tenant en Base de Datos**
```sql
INSERT INTO tenant_clients (id, name, slug) 
VALUES ('nueva-tienda-2024', 'Nueva Tienda', 'nueva-tienda');
```

### **2. Configurar Subdominio**
```
https://nueva-tienda.sintestesia.cl → IP del servidor
```

### **3. Configurar Twilio (Opcional)**
```sql
INSERT INTO twilio_accounts (tenant_id, account_sid, auth_token_enc, from_number)
VALUES ('nueva-tienda-2024', 'AC...', 'encrypted_token', '+14155238886');
```

### **4. URLs Automáticas**
- **Twilio:** `https://nueva-tienda.sintestesia.cl/bot/twilio/webhook`
- **API:** `http://localhost:9001/webhook/nueva-tienda`

### **5. ¡Listo!**
El sistema detecta automáticamente el nuevo cliente sin código adicional.

---

## 🔧 CONFIGURACIÓN EN TWILIO

### **Para cada cliente:**

1. **Ir a Twilio Console → Phone Numbers**
2. **Seleccionar número de WhatsApp del cliente**
3. **Configurar webhook:**
   ```
   Webhook URL: https://{slug}.sintestesia.cl/bot/twilio/webhook
   HTTP Method: POST
   ```

### **Ejemplos:**
- ACME: `https://acme.sintestesia.cl/bot/twilio/webhook`
- Bravo: `https://bravo.sintestesia.cl/bot/twilio/webhook`
- Mundo Canino: `https://mundo-canino.sintestesia.cl/bot/twilio/webhook`

---

## ✅ VENTAJAS DEL SISTEMA

### **🎯 Completamente Dinámico**
- No hay código hardcodeado para clientes específicos
- Nuevos clientes se agregan solo con configuración de BD

### **🔒 Aislamiento por Tenant**
- Cada cliente solo ve sus productos
- Configuración Twilio independiente por cliente
- Datos completamente separados

### **📈 Escalable**
- Soporta cantidad ilimitada de clientes
- Detección automática de nuevos tenants
- Sistema de URLs consistente

### **🛠️ Mantenible**
- Un solo endpoint maneja todos los clientes
- Lógica centralizada y reutilizable
- Fácil debugging por cliente

### **🔄 Flexible**
- Soporta múltiples proveedores (Twilio, Meta)
- URLs por subdominio y por slug
- Compatibilidad con sistemas legacy

---

## 🧪 TESTING

### **Test Tenant ACME**
```bash
curl -X POST "http://localhost:9001/webhook/acme" \
  -H "Content-Type: application/json" \
  -d '{"telefono": "+56950915617", "mensaje": "northern lights"}'
```

### **Test Tenant Bravo**
```bash
curl -X POST "http://localhost:9001/webhook/bravo" \
  -H "Content-Type: application/json" \
  -d '{"telefono": "+56999888777", "mensaje": "que consolas tienes"}'
```

### **Listar Todos los Tenants**
```bash
curl http://localhost:9001/tenants
```

---

## 📚 DOCUMENTACIÓN RELACIONADA

- **DEPLOYMENT_GUIDE.md** - Guía completa de despliegue
- **CHANGELOG_BOT_IMPROVEMENTS.md** - Historial de cambios
- **DETAILED_FUNCTION_CHANGES.md** - Cambios técnicos detallados

---

**✅ ESTADO:** Sistema Multi-tenant Completamente Funcional  
**🔧 MANTENIMIENTO:** Automático via base de datos  
**📈 ESCALABILIDAD:** Ilimitada - Solo requiere configuración DNS

---

## 🎯 **CONFIGURACIÓN ACTUAL VERIFICADA**

### **ACME Cannabis - ✅ FUNCIONANDO**
- **Twilio Webhook:** `https://acme.sintestesia.cl/bot/twilio/webhook`
- **API Webhook:** `http://localhost:9001/webhook/acme`
- **Tenant ID:** `acme-cannabis-2024`
- **Detección:** ✅ Automática por subdominio y slug

### **Sistema Listo para Nuevos Clientes**
Solo necesitas:
1. Crear entrada en `tenant_clients`
2. Configurar DNS para subdominio
3. ¡El webhook funciona automáticamente!