# Configuración Nginx para Subdominios Multi-Tenant

## 🚨 Problema Actual

Los subdominios `acme.sintestesia.cl` y `bravo.sintestesia.cl` están dando **404 Not Found** porque nginx no tiene configuración para enrutarlos.

**DNS Status:** ✅ Ambos resuelven a `31.97.162.56` correctamente
**Backend Status:** ✅ Middleware funciona perfectamente con headers
**Nginx Status:** ❌ No configurado para nuevos subdominios

## 🔧 Configuración Nginx Requerida

### Opción 1: Enrutar al Frontend (Recomendado)

```nginx
# /etc/nginx/sites-available/acme-sintestesia
server {
    listen 80;
    listen 443 ssl http2;
    server_name acme.sintestesia.cl;
    
    # SSL configuration (usar mismo cert que sintestesia.cl)
    ssl_certificate /path/to/sintestesia.cl.crt;
    ssl_certificate_key /path/to/sintestesia.cl.key;
    
    # Forward to frontend with Host header preserved
    location / {
        proxy_pass http://localhost:8080;  # Frontend container
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # API calls forward to backend
    location /api/ {
        proxy_pass http://localhost:8002;  # Backend container
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# /etc/nginx/sites-available/bravo-sintestesia
server {
    listen 80;
    listen 443 ssl http2;
    server_name bravo.sintestesia.cl;
    
    # SSL configuration
    ssl_certificate /path/to/sintestesia.cl.crt;
    ssl_certificate_key /path/to/sintestesia.cl.key;
    
    # Forward to frontend with Host header preserved
    location / {
        proxy_pass http://localhost:8080;  # Frontend container
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # API calls forward to backend  
    location /api/ {
        proxy_pass http://localhost:8002;  # Backend container
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_Set_header X-Forwarded-Proto $scheme;
    }
}
```

### Opción 2: Wildcard Config (Más Simple)

```nginx
# /etc/nginx/sites-available/wildcard-sintestesia
server {
    listen 80;
    listen 443 ssl http2;
    server_name *.sintestesia.cl;
    
    # SSL configuration
    ssl_certificate /path/to/sintestesia.cl-wildcard.crt;
    ssl_certificate_key /path/to/sintestesia.cl-wildcard.key;
    
    # Frontend
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_Set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🚀 Pasos para Implementar

### 1. Crear Configuración Nginx

```bash
# Crear archivos de configuración
sudo nano /etc/nginx/sites-available/acme-sintestesia
sudo nano /etc/nginx/sites-available/bravo-sintestesia

# Habilitar sitios
sudo ln -s /etc/nginx/sites-available/acme-sintestesia /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/bravo-sintestesia /etc/nginx/sites-enabled/

# Verificar configuración
sudo nginx -t

# Reiniciar nginx
sudo systemctl reload nginx
```

### 2. Configurar SSL (si no tienes wildcard)

```bash
# Usar certbot para nuevos subdominios
sudo certbot --nginx -d acme.sintestesia.cl -d bravo.sintestesia.cl
```

### 3. Verificar Frontend

El frontend debe estar configurado para detectar el subdominio y usar la API correcta:

```javascript
// En frontend - auto-detect tenant
const hostname = window.location.hostname;
const subdomain = hostname.split('.')[0];
const tenantId = subdomain; // acme, bravo

// Configure API calls to include Host header
const apiHeaders = {
    'Host': hostname,  // acme.sintestesia.cl
    'Content-Type': 'application/json'
};
```

## 🧪 Testing Después de Configurar

```bash
# Test que deben funcionar después de nginx config:
curl https://acme.sintestesia.cl/
curl https://bravo.sintestesia.cl/
curl https://acme.sintestesia.cl/api/health
curl https://bravo.sintestesia.cl/api/health
```

## ⚡ Solución Temporal (Para Testing Inmediato)

Si necesitas probar ahora mismo sin configurar nginx:

```bash
# Test directo al backend (esto ya funciona)
curl -H "Host: acme.sintestesia.cl" https://api.sintestesia.cl/api/products
curl -H "Host: bravo.sintestesia.cl" https://api.sintestesia.cl/api/products

# Test con frontend local
echo "127.0.0.1 acme.sintestesia.cl" >> /etc/hosts
echo "127.0.0.1 bravo.sintestesia.cl" >> /etc/hosts

# Luego acceder a:
# http://acme.sintestesia.cl:8080 (frontend directo)
# http://acme.sintestesia.cl:8002 (backend directo)
```

## 📋 Estado Actual

- ✅ **DNS configurado:** acme/bravo → 31.97.162.56
- ✅ **Backend preparado:** Middleware multi-tenant funcional
- ✅ **Cuentas creadas:** Ambas cuentas en base de datos
- ❌ **Nginx config:** Falta configuración para nuevos subdominios

**Próximo paso:** Configurar nginx para enrutar los subdominios al stack de la aplicación.

---

¿Tienes acceso al servidor para configurar nginx, o necesitas que prepare instrucciones más específicas?