# 🔐 Sistema de Login Multi-Tenant

## ✅ Implementación Completada

Se ha implementado exitosamente un sistema de autenticación multi-tenant completo para el backoffice e-commerce con las siguientes características:

### 🏗️ Arquitectura

**Backend (FastAPI + SQLAlchemy)**
- ✅ Modelo multi-tenant con una sola base de datos
- ✅ Autenticación JWT con refresh tokens
- ✅ Middleware de resolución de tenant automático
- ✅ Filtrado automático de queries por `client_id`
- ✅ Aislamiento total entre tenants

**Frontend (React + TypeScript)**
- ✅ AuthContext con manejo automático de tokens
- ✅ ProtectedRoute para rutas privadas
- ✅ Auto-refresh de access tokens
- ✅ UI de login/registro responsiva

### 📊 Estructura de Base de Datos

```sql
-- Clientes (tenants)
tenant_clients (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP
)

-- Usuarios con tenant isolation
tenant_users (
    id UUID PRIMARY KEY,
    client_id UUID REFERENCES tenant_clients(id),
    email TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'user', -- 'owner', 'admin', 'user'
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP,
    UNIQUE(client_id, email)
)

-- Órdenes tenant-aware
tenant_orders (
    id UUID PRIMARY KEY,
    client_id UUID REFERENCES tenant_clients(id),
    code TEXT NOT NULL, -- Único por tenant
    customer_name TEXT NOT NULL,
    total TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP,
    UNIQUE(client_id, code)
)
```

### 🔑 Endpoints de Autenticación

**Registro**
```http
POST /auth/register
{
    "email": "admin@empresa.com",
    "password": "password123",
    "client_name": "Mi Empresa SpA"  // Crea nueva empresa
}
```

**Registro en empresa existente**
```http
POST /auth/register
{
    "email": "usuario@empresa.com", 
    "password": "password123",
    "client_slug": "mi-empresa"     // Usa empresa existente
}
```

**Login**
```http
POST /auth/login
{
    "email": "admin@empresa.com",
    "password": "password123",
    "client_slug": "mi-empresa"     // Opcional
}
```

**Refresh Token**
```http
POST /auth/refresh
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Usuario Actual**
```http
GET /auth/me
Authorization: Bearer <access_token>
```

### 🏢 Endpoints Tenant-Aware

**Órdenes por Tenant**
```http
GET /api/tenant-orders/
Authorization: Bearer <access_token>
```

```http
POST /api/tenant-orders/
Authorization: Bearer <access_token>
{
    "code": "ORD-001",
    "customer_name": "Juan Pérez",
    "total": "15000.00",
    "status": "pending"
}
```

### 🛡️ Seguridad y Aislamiento

1. **Aislamiento por JWT**: Cada token contiene `client_id` del usuario
2. **Filtrado automático**: Todas las queries se filtran por `client_id`
3. **Validación de headers**: Soporte opcional para `X-Client-Slug`
4. **Constraints únicos**: Códigos únicos por tenant (no globalmente)
5. **Roles por tenant**: `owner`, `admin`, `user`

### 🧪 Datos Demo

```bash
# Crear datos de prueba
cd backend
python seed_multi_tenant.py
```

**Credenciales de Demo:**

**Demo Company (demo)**
- Email: `admin@demo.com` | Password: `demo123` | Role: `owner`
- Email: `user@demo.com` | Password: `demo123` | Role: `user`

**Test Store (test-store)**
- Email: `admin@teststore.com` | Password: `test123` | Role: `owner`

### 🚀 Comandos para Ejecutar

**Backend**
```bash
cd backend

# Instalar dependencias
pip install fastapi uvicorn sqlalchemy alembic bcrypt python-jose[cryptography] passlib[bcrypt]

# Ejecutar migraciones
alembic upgrade head

# Crear datos demo
python seed_multi_tenant.py

# Iniciar servidor
uvicorn main:app --reload --port 8002
```

**Frontend**
```bash
cd frontend

# Instalar dependencias (ya instaladas)
npm install

# Iniciar desarrollo
npm run dev -- --host 127.0.0.1 --port 3000
```

### 🌐 Acceso

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8002/docs
- **Backend**: http://localhost:8002

### 📝 Flujo de Usuario

1. **Registro**: Usuario crea cuenta y empresa, o se une a empresa existente
2. **Login**: Usuario ingresa credenciales y recibe tokens JWT
3. **Navegación**: Frontend usa tokens automáticamente en todas las requests
4. **Auto-refresh**: Tokens se renuevan automáticamente antes de expirar
5. **Aislamiento**: Solo ve datos de su empresa, nunca de otras

### 🔍 Validación de Aislamiento

```python
# Ejecutar tests de aislamiento
python test_multi_tenant.py
```

Los tests validan:
- ✅ Registro y login funcional
- ✅ Aislamiento total entre tenants
- ✅ Constraints únicos por tenant
- ✅ Acceso denegado entre tenants
- ✅ Refresh tokens funcionando

### 💡 Características Técnicas

**JWT Claims**
```json
{
    "sub": "user_id",
    "client_id": "client_uuid", 
    "role": "owner|admin|user",
    "exp": 1641234567,
    "iat": 1641230967
}
```

**Auto-refresh Logic**
- Access token: 15 minutos
- Refresh token: 7 días  
- Auto-refresh cuando quedan < 60 segundos

**Helper Functions**
```python
# Filtrado automático de queries
def tenant_filter_query(query, model, client_id: str):
    if hasattr(model, 'client_id'):
        return query.filter(model.client_id == client_id)
    return query
```

### 🎯 Estado Actual

✅ **Completamente funcional** - Sistema multi-tenant listo para producción  
✅ **Frontend integrado** - Login/logout con auto-refresh  
✅ **Backend seguro** - Aislamiento garantizado entre tenants  
✅ **Datos demo** - Listo para pruebas inmediatas  
✅ **Tests validados** - Aislamiento multi-tenant confirmado  

El sistema está listo para usar. Accede a http://localhost:3000 y usa cualquiera de las credenciales demo para iniciar sesión.