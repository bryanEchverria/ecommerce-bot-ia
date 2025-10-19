# 📱 WhatsApp Multi-Tenant E-commerce Bot - Documentación Completa

## 📋 Tabla de Contenidos
1. [Visión General](#visión-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Estructura de Directorios](#estructura-de-directorios)
4. [API Endpoints y Rutas](#api-endpoints-y-rutas)
5. [Flujo de Procesamiento de Mensajes](#flujo-de-procesamiento-de-mensajes)
6. [Sistema Multi-Tenant](#sistema-multi-tenant)
7. [Motor de Inteligencia Artificial](#motor-de-inteligencia-artificial)
8. [Base de Datos](#base-de-datos)
9. [Configuración y Deployment](#configuración-y-deployment)
10. [Ejemplos de Uso](#ejemplos-de-uso)
11. [Testing y Debug](#testing-y-debug)
12. [Troubleshooting](#troubleshooting)

---

## 🎯 Visión General

### ¿Qué es?
Un bot de WhatsApp inteligente multi-tenant para e-commerce que permite a múltiples negocios tener su propio asistente virtual personalizado. Utiliza GPT-4o-mini para procesamiento de lenguaje natural y respuestas contextuales.

### Características Principales
- ✅ **Multi-tenant**: Soporta múltiples negocios en una sola instalación
- ✅ **IA Avanzada**: Motor GPT con razonamiento dinámico
- ✅ **100% Personalizable**: Prompts, estilos y configuración por tenant
- ✅ **Dual Provider**: Soporta Meta Cloud API y Twilio
- ✅ **Escalable**: Arquitectura asíncrona con FastAPI
- ✅ **Seguro**: Aislamiento estricto de datos por tenant

### Stack Tecnológico
- **Backend**: FastAPI (Python 3.9+)
- **IA**: OpenAI GPT-4o-mini
- **Base de Datos**: PostgreSQL
- **WhatsApp**: Meta Cloud API / Twilio
- **Frontend Admin**: Next.js + React
- **Deployment**: Docker + Docker Compose

---

## 🏗️ Arquitectura del Sistema

### Diagrama de Arquitectura
```
┌─────────────────────────────────────────────────────────────┐
│                     CAPA DE ENTRADA                          │
├─────────────────────────────────────────────────────────────┤
│  WhatsApp Users  →  Meta/Twilio  →  Webhooks               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     CAPA DE APLICACIÓN                       │
├─────────────────────────────────────────────────────────────┤
│  FastAPI Main App (Port 9001)                               │
│  ├── Webhook Routers                                        │
│  ├── Chat Service                                           │
│  └── Tenant Manager                                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     CAPA DE INTELIGENCIA                     │
├─────────────────────────────────────────────────────────────┤
│  GPT Reasoning Engine                                        │
│  ├── Intent Detection                                       │
│  ├── Context Analysis                                       │
│  └── Response Generation                                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     CAPA DE DATOS                           │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL Database                                        │
│  ├── Products & Inventory                                   │
│  ├── Tenant Configuration                                   │
│  ├── Session Management                                     │
│  └── Order Processing                                       │
└─────────────────────────────────────────────────────────────┘
```

### Componentes Principales

#### 1. **WhatsApp Bot Service** (Puerto 9001)
- Recibe webhooks de WhatsApp
- Procesa mensajes con IA
- Gestiona sesiones de usuarios

#### 2. **Backend API** (Puerto 8000)
- Administración de tenants
- Configuración de prompts
- Gestión de productos

#### 3. **Frontend Admin** (Puerto 3000)
- Panel de administración
- Configuración visual del bot
- Analytics y reportes

---

## 📁 Estructura de Directorios

```
/root/ecommerce-platform/
├── ecommerce-bot-ia/
│   ├── whatsapp-bot-fastapi/       # 🤖 Bot principal
│   │   ├── main.py                 # Entry point FastAPI
│   │   ├── api/                    # Routers de webhooks
│   │   │   ├── webhook_meta.py     # Meta WhatsApp webhook
│   │   │   └── webhook_twilio.py   # Twilio webhook
│   │   ├── services/               # Lógica de negocio
│   │   │   ├── gpt_reasoning_engine.py    # Motor IA principal
│   │   │   ├── ai_improvements.py         # Funciones IA mejoradas
│   │   │   ├── flow_chat_service.py       # Servicio de chat
│   │   │   ├── chat_service.py            # Procesamiento mensajes
│   │   │   ├── tenant_config_manager.py   # Config multi-tenant
│   │   │   └── backoffice_integration.py  # Integración backend
│   │   ├── models.py               # Modelos SQLAlchemy
│   │   ├── database.py             # Configuración DB
│   │   └── requirements.txt        # Dependencias
│   │
│   ├── backend/                    # 🔧 API Backend
│   │   ├── main.py                 # FastAPI backend
│   │   ├── prompt_schemas.py       # Esquemas de configuración
│   │   ├── routers/
│   │   │   ├── tenant_prompts.py   # API de prompts
│   │   │   └── whatsapp_settings.py # Config WhatsApp
│   │   └── services/
│   │       └── tenant_prompt_cache.py  # Cache de prompts
│   │
│   └── frontend/                   # 💻 Panel Admin
│       ├── components/
│       │   ├── BotConfiguration.tsx
│       │   └── BotConfigurationWithChat.tsx
│       └── pages/
│           └── bot-config.tsx
│
├── docker-compose.yml              # 🐳 Configuración Docker
└── .env                           # 🔐 Variables de entorno
```

---

## 🚀 API Endpoints y Rutas

### WhatsApp Bot Service (Puerto 9001)

#### 1. **Webhook de Meta WhatsApp**
```http
GET /webhook/meta
```
**Descripción**: Verificación del webhook de Meta
**Parámetros Query**:
- `hub.mode`: Debe ser "subscribe"
- `hub.verify_token`: Token de verificación
- `hub.challenge`: Challenge a retornar

**Ejemplo**:
```bash
curl -X GET "http://localhost:9001/webhook/meta?hub.mode=subscribe&hub.verify_token=tu_token&hub.challenge=test123"
```

---

```http
POST /webhook/meta
```
**Descripción**: Recibe mensajes de Meta WhatsApp Cloud API
**Headers**:
- `X-Hub-Signature-256`: Firma del webhook (opcional)

**Body**:
```json
{
  "object": "whatsapp_business_account",
  "entry": [{
    "changes": [{
      "field": "messages",
      "value": {
        "messages": [{
          "from": "56912345678",
          "text": {"body": "Hola"},
          "timestamp": "1234567890"
        }]
      }
    }]
  }]
}
```

---

#### 2. **Webhook Multi-Tenant Dinámico**
```http
POST /webhook/{tenant_slug}
```
**Descripción**: Webhook específico por tenant
**Parámetros**:
- `tenant_slug`: Slug del tenant (ej: "acme", "bravo")

**Body**:
```json
{
  "telefono": "+56912345678",
  "mensaje": "Quiero ver productos",
  "historial": []
}
```

**Response**:
```json
{
  "telefono": "+56912345678",
  "mensaje_usuario": "Quiero ver productos",
  "respuesta": "¡Hola! 🌿 Tenemos estos productos disponibles:\n1. Northern Lights - $15,000\n2. Blue Dream - $18,000",
  "tenant_slug": "acme",
  "tenant_id": "acme-cannabis-2024",
  "tenant_name": "Acme Cannabis",
  "status": "success"
}
```

---

#### 3. **Chat con Contexto**
```http
POST /chat
```
**Descripción**: Chat con historial de conversación
**Body**:
```json
{
  "telefono": "+56912345678",
  "mensaje": "¿Cuánto cuesta?",
  "historial": [
    {"user": "Hola", "bot": "¡Hola! Bienvenido a Acme Cannabis"},
    {"user": "Quiero Northern Lights", "bot": "Northern Lights cuesta $15,000"}
  ]
}
```

---

#### 4. **Listar Tenants Disponibles**
```http
GET /tenants
```
**Response**:
```json
{
  "status": "success",
  "total_tenants": 3,
  "tenants": [
    {
      "id": "acme-cannabis-2024",
      "name": "Acme Cannabis",
      "slug": "acme",
      "webhook_url": "/webhook/acme",
      "full_webhook_url": "http://localhost:9001/webhook/acme",
      "status": "active"
    }
  ]
}
```

---

### Backend API Service (Puerto 8000)

#### 1. **Configuración de Prompts**

```http
GET /api/tenants/{tenant_id}/prompt
```
**Descripción**: Obtiene configuración actual del bot
**Headers**: `Authorization: Bearer {token}`

---

```http
PUT /api/tenants/{tenant_id}/prompt
```
**Descripción**: Actualiza configuración del bot
**Body**:
```json
{
  "system_prompt": "Eres un asistente de ventas especializado...",
  "style_overrides": {
    "tono": "amigable",
    "usar_emojis": true,
    "emojis_permitidos": ["🌿", "✅", "🛒"],
    "cta_principal": "¡Compra ahora!",
    "limite_respuesta_caracteres": 500
  },
  "nlu_params": {
    "modelo": "gpt-4o-mini",
    "temperature_nlu": 0.3,
    "max_tokens_nlu": 150
  },
  "nlg_params": {
    "modelo": "gpt-4o-mini",
    "temperature_nlg": 0.7,
    "max_tokens_nlg": 300
  }
}
```

---

```http
POST /api/tenants/{tenant_id}/prompt/preview
```
**Descripción**: Preview de respuesta sin guardar cambios
**Body**:
```json
{
  "prompt_config": {
    "system_prompt": "Eres un vendedor experto...",
    "style_overrides": {"tono": "profesional"}
  },
  "test_message": "Hola, ¿qué productos tienen?",
  "include_products": true
}
```

---

## 🔄 Flujo de Procesamiento de Mensajes

### Flujo Detallado Paso a Paso

```mermaid
graph TD
    A[Usuario envía mensaje WhatsApp] --> B[WhatsApp Provider Meta/Twilio]
    B --> C[Webhook Endpoint]
    C --> D{Identificar Tenant}
    D --> E[Cargar Configuración Tenant]
    E --> F[Obtener Sesión Usuario]
    F --> G[Cargar Productos BD]
    G --> H[GPT Reasoning Engine]
    H --> I[Detectar Intención]
    I --> J[Generar Respuesta]
    J --> K[Aplicar Estilo Tenant]
    K --> L[Enviar a WhatsApp]
    L --> M[Actualizar Sesión]
```

### Código del Flujo Principal

```python
# whatsapp-bot-fastapi/services/flow_chat_service.py

def procesar_mensaje_flow(db: Session, telefono: str, mensaje: str, tenant_id: str) -> str:
    """
    Flujo principal de procesamiento de mensajes
    """
    # 1. Validar tenant
    tenant_id = _validate_tenant_id(tenant_id)
    
    # 2. Obtener información del tenant
    tenant_info = get_tenant_info(db, tenant_id)
    
    # 3. Cargar productos del inventario
    productos = get_real_products_from_backoffice(db, tenant_id)
    
    # 4. Obtener/crear sesión del usuario
    sesion = obtener_o_crear_sesion(db, telefono, tenant_id)
    
    # 5. Procesar con GPT Reasoning Engine
    engine = GPTReasoningEngine(db, tenant_id, productos)
    respuesta = engine.process_message_with_pure_gpt_reasoning(
        telefono, 
        mensaje
    )
    
    # 6. Actualizar sesión
    actualizar_sesion(db, sesion, mensaje, respuesta)
    
    return respuesta
```

---

## 👥 Sistema Multi-Tenant

### 🚀 **Concepto Clave: Webhooks Únicos por Cliente**

El bot es **100% multi-tenant**, esto significa que:

✅ **Cada cliente tiene su propia URL de webhook única**
✅ **Cada cliente configura su cuenta WhatsApp independiente** 
✅ **Aislamiento total de datos, productos y configuración**
✅ **Un solo servidor maneja múltiples clientes sin interferencia**

#### **Ejemplo de Configuración Multi-Tenant:**

```yaml
# Cliente 1: ACME Cannabis
Empresa: ACME Cannabis
WhatsApp Number: +1234567890
Webhook URL: https://tudominio.com/webhook/acme
Productos: Cannabis, aceites, semillas
Configuración: Tono casual, emojis 🌿

# Cliente 2: Bravo Gaming  
Empresa: Bravo Gaming
WhatsApp Number: +0987654321
Webhook URL: https://tudominio.com/webhook/bravo
Productos: Videojuegos, consolas, accesorios
Configuración: Tono gamer, emojis 🎮

# Cliente 3: Mundo Canino
Empresa: Mundo Canino
WhatsApp Number: +1122334455
Webhook URL: https://tudominio.com/webhook/mundo-canino
Productos: Comida perros, juguetes, accesorios
Configuración: Tono amigable, emojis 🐕
```

#### **Flujo Multi-Tenant Explicado:**

```mermaid
graph LR
    A[Cliente ACME<br/>+1234567890] --> B[Meta/Twilio]
    C[Cliente Bravo<br/>+0987654321] --> D[Meta/Twilio]
    E[Cliente Mundo Canino<br/>+1122334455] --> F[Meta/Twilio]
    
    B --> G[/webhook/acme]
    D --> H[/webhook/bravo]
    F --> I[/webhook/mundo-canino]
    
    G --> J[Bot ACME<br/>🌿 Cannabis]
    H --> K[Bot Bravo<br/>🎮 Gaming]
    I --> L[Bot Mundo Canino<br/>🐕 Pets]
```

#### **URLs de Webhooks Activos:**

Puedes ver todos los tenants disponibles:
```bash
curl http://localhost:9001/tenants
```

**Respuesta actual del sistema:**
```json
{
  "total_tenants": 5,
  "tenants": [
    {
      "name": "ACME Cannabis Store",
      "slug": "acme", 
      "webhook_url": "/webhook/acme",
      "full_webhook_url": "http://localhost:9001/webhook/acme"
    },
    {
      "name": "Bravo Gaming Store", 
      "slug": "bravo",
      "webhook_url": "/webhook/bravo",
      "full_webhook_url": "http://localhost:9001/webhook/bravo"
    },
    {
      "name": "Mundo Canino Store",
      "slug": "mundo-canino", 
      "webhook_url": "/webhook/mundo-canino",
      "full_webhook_url": "http://localhost:9001/webhook/mundo-canino"
    }
  ]
}
```

### Configuración de Nuevo Tenant

#### 1. Crear Tenant en Base de Datos
```sql
-- Insertar nuevo tenant
INSERT INTO tenant_clients (id, name, slug, created_at) 
VALUES (
    'nueva-tienda-2024',
    'Nueva Tienda',
    'nueva',
    NOW()
);

-- Configurar cuenta WhatsApp (Twilio)
INSERT INTO twilio_accounts (
    id, 
    tenant_id, 
    account_sid, 
    auth_token_enc, 
    from_number
) VALUES (
    'twilio-nueva-tienda',
    'nueva-tienda-2024',
    'AC...',  -- Account SID de Twilio
    'encrypted_token',
    'whatsapp:+14155238886'
);
```

#### 2. Configurar Prompts Iniciales
```python
# Script Python para configurar tenant
import requests

config = {
    "system_prompt": """
    Eres el asistente virtual de Nueva Tienda.
    Especializado en [tipo de productos].
    Siempre sé amable y profesional.
    """,
    "style_overrides": {
        "tono": "profesional",
        "usar_emojis": True,
        "limite_respuesta_caracteres": 400
    }
}

response = requests.put(
    f"http://localhost:8000/api/tenants/nueva-tienda-2024/prompt",
    json=config,
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
```

#### 3. Configurar Webhook Único del Nuevo Tenant

**🎯 IMPORTANTE: Cada tenant tiene su propia URL de webhook única**

```
Webhook URL para Nueva Tienda: https://tudominio.com/webhook/nueva
```

**Configuración en WhatsApp Provider:**

Para **Meta WhatsApp Cloud API**:
```bash
# Configurar webhook en Meta Developer Console
Webhook URL: https://tudominio.com/webhook/nueva
Verify Token: tu_token_verificacion
Webhook Fields: messages, messaging_postbacks
```

Para **Twilio WhatsApp**:
```bash
# Configurar en Twilio Console
Webhook URL: https://tudominio.com/webhook/nueva
HTTP Method: POST
Content Type: application/json
```

**Test del Webhook:**
```bash
# Test directo al webhook del nuevo tenant
curl -X POST https://tudominio.com/webhook/nueva \
  -H "Content-Type: application/json" \
  -d '{
    "telefono": "+56912345678",
    "mensaje": "Hola, soy cliente nuevo"
  }'

# Respuesta esperada:
{
  "respuesta": "¡Hola! Bienvenido a Nueva Tienda...",
  "tenant_slug": "nueva",
  "tenant_id": "nueva-tienda-2024",
  "tenant_name": "Nueva Tienda",
  "status": "success"
}
```

### Aislamiento de Datos

Todas las tablas tienen campo `tenant_id` o `client_id`:

```python
# Ejemplo de query con aislamiento
def get_products_for_tenant(db: Session, tenant_id: str):
    return db.query(Product).filter(
        Product.client_id == tenant_id,
        Product.status == "Active"
    ).all()
```

---

## 🧠 Motor de Inteligencia Artificial

### GPT Reasoning Engine

El motor toma decisiones 100% dinámicas sin condicionales hardcodeados:

```python
# gpt_reasoning_engine.py

class GPTReasoningEngine:
    def process_message_with_pure_gpt_reasoning(self, telefono: str, mensaje: str) -> str:
        """
        Procesamiento con razonamiento GPT puro
        """
        # 1. GPT decide qué hacer
        action_decision = self._ask_gpt_what_to_do(mensaje)
        
        # 2. GPT ejecuta la acción
        response = self._ask_gpt_to_execute_action(action_decision, mensaje)
        
        # 3. GPT formatea la respuesta
        final_response = self._ask_gpt_to_format_response(response)
        
        return final_response
```

### Proceso de Decisión

```python
def _ask_gpt_what_to_do(self, mensaje: str) -> Dict[str, Any]:
    """
    GPT analiza y decide la acción apropiada
    """
    decision_prompt = f"""
    Eres el cerebro de {self.tenant_config.business_name}.
    
    MENSAJE: "{mensaje}"
    
    OPCIONES DE ACCIÓN:
    1. "respuesta_directa" - Responder sin consultar productos
    2. "buscar_productos" - Buscar productos específicos
    3. "mostrar_categoria" - Mostrar categoría
    4. "mostrar_catalogo" - Catálogo completo
    5. "consulta_compleja" - Análisis profundo
    
    RESPONDE EN JSON con tu decisión y razonamiento.
    """
    
    # GPT retorna decisión estructurada
    return gpt_response
```

### Detección de Intención

```python
# ai_improvements.py

def gpt_detect_intent(
    tenant_id: str,
    store_name: str, 
    mensaje: str,
    history: List,
    productos: List[Dict],
    db: Session
) -> Dict:
    """
    Detecta intención usando GPT con contexto del negocio
    """
    prompt = f"""
    Analiza el mensaje para {store_name}.
    
    CONTEXTO:
    - Productos disponibles: {len(productos)}
    - Historial: {history}
    
    MENSAJE: "{mensaje}"
    
    DETECTA:
    1. Intención principal
    2. Entidades mencionadas
    3. Contexto requerido
    4. Acción sugerida
    """
    
    return gpt_analysis
```

---

## 🗄️ Base de Datos

### Esquema de Tablas Principales

#### 1. **products** - Catálogo de Productos
```sql
CREATE TABLE products (
    id VARCHAR PRIMARY KEY,
    name VARCHAR,
    description TEXT,
    category VARCHAR,
    price FLOAT,
    sale_price FLOAT,
    stock INTEGER,
    status VARCHAR,
    client_id VARCHAR NOT NULL,  -- Multi-tenant
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### 2. **tenant_clients** - Información de Tenants
```sql
CREATE TABLE tenant_clients (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    slug VARCHAR UNIQUE NOT NULL,
    created_at TIMESTAMP
);
```

#### 3. **tenant_prompts** - Configuración de Bots
```sql
CREATE TABLE tenant_prompts (
    id VARCHAR PRIMARY KEY,
    tenant_id VARCHAR NOT NULL,
    system_prompt TEXT,
    style_overrides JSONB,
    nlu_params JSONB,
    nlg_params JSONB,
    version INTEGER,
    is_active BOOLEAN,
    updated_by VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### 4. **flow_sesiones** - Sesiones de Chat
```sql
CREATE TABLE flow_sesiones (
    id SERIAL PRIMARY KEY,
    telefono VARCHAR UNIQUE,
    tenant_id VARCHAR NOT NULL,
    estado VARCHAR DEFAULT 'INITIAL',
    datos TEXT,  -- JSON con datos de sesión
    last_message_at TIMESTAMP,
    conversation_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Queries Comunes

```python
# Obtener productos activos de un tenant
query = text("""
    SELECT * FROM products 
    WHERE client_id = :tenant_id 
    AND status = 'Active' 
    AND stock > 0
    ORDER BY name
""")
result = db.execute(query, {"tenant_id": tenant_id})

# Obtener sesión activa
sesion = db.query(FlowSesion).filter(
    FlowSesion.telefono == telefono,
    FlowSesion.tenant_id == tenant_id,
    FlowSesion.conversation_active == True
).first()
```

---

## ⚙️ Configuración y Deployment

### Variables de Entorno (.env)

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/dbname

# WhatsApp Meta
WHATSAPP_VERIFY_TOKEN=tu_token_verificacion
WHATSAPP_ACCESS_TOKEN=EAA...
WHATSAPP_PHONE_NUMBER_ID=123456789

# WhatsApp Twilio
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Backend
BACKEND_URL=http://localhost:8000
JWT_SECRET_KEY=tu_secret_key

# Ports
BOT_PORT=9001
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: ecommerce_multi_tenant
      POSTGRES_USER: ecommerce_user
      POSTGRES_PASSWORD: ecommerce123
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  whatsapp-bot:
    build: ./ecommerce-bot-ia/whatsapp-bot-fastapi
    ports:
      - "9001:9001"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - postgres

  backend:
    build: ./ecommerce-bot-ia/backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - postgres

  frontend:
    build: ./ecommerce-bot-ia/frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Comandos de Deployment

```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f whatsapp-bot

# Reiniciar servicio
docker-compose restart whatsapp-bot

# Ejecutar migraciones
docker-compose exec backend alembic upgrade head

# Acceder a la base de datos
docker-compose exec postgres psql -U ecommerce_user -d ecommerce_multi_tenant
```

---

## 📚 Ejemplos de Uso

### Ejemplo 1: Conversación Multi-Tenant

#### **Cliente ACME Cannabis** (webhook: `/webhook/acme`)
```bash
# Usuario de ACME Cannabis pregunta por aceites
curl -X POST http://localhost:9001/webhook/acme \
  -H "Content-Type: application/json" \
  -d '{
    "telefono": "+56912345678",
    "mensaje": "Hola, quiero ver aceites"
  }'

# Respuesta de ACME (tono cannabis, productos específicos):
{
  "respuesta": "¡Hola! 🌿 Te muestro nuestros aceites cannábicos:\n\n1. **Aceite CBD 500mg** - $25,000\n   Extracto puro para uso medicinal\n   ✅ 15 unidades disponibles\n\n2. **Aceite Full Spectrum** - $35,000\n   Espectro completo THC+CBD\n   ✅ 8 unidades disponibles\n\n¿Cuál necesitas? 💚",
  "tenant_slug": "acme",
  "tenant_name": "ACME Cannabis Store"
}
```

#### **Cliente Bravo Gaming** (webhook: `/webhook/bravo`)
```bash
# Usuario de Bravo Gaming pregunta por productos
curl -X POST http://localhost:9001/webhook/bravo \
  -H "Content-Type: application/json" \
  -d '{
    "telefono": "+56987654321", 
    "mensaje": "Hola, qué consolas tienen?"
  }'

# Respuesta de Bravo (tono gamer, productos gaming):
{
  "respuesta": "¡Hola gamer! 🎮 Estas son nuestras consolas disponibles:\n\n1. **PlayStation 5** - $599,990\n   La consola next-gen de Sony\n   ✅ 3 unidades disponibles\n\n2. **Xbox Series X** - $549,990\n   Potencia 4K de Microsoft\n   ✅ 5 unidades disponibles\n\n¿Cuál te llama más? 🕹️",
  "tenant_slug": "bravo", 
  "tenant_name": "Bravo Gaming Store"
}
```

#### **Cliente Mundo Canino** (webhook: `/webhook/mundo-canino`)
```bash
# Usuario de Mundo Canino pregunta por comida
curl -X POST http://localhost:9001/webhook/mundo-canino \
  -H "Content-Type: application/json" \
  -d '{
    "telefono": "+56900000000",
    "mensaje": "Qué comida tienen para perros?"
  }'

# Respuesta de Mundo Canino (tono pet-friendly):
{
  "respuesta": "¡Hola! 🐕 Tenemos estas opciones de alimento:\n\n1. **Royal Canin Adult** - $45,000\n   Nutrición balanceada para adultos\n   ✅ 20 sacos disponibles\n\n2. **Pedigree Cachorro** - $28,000\n   Especial para perritos pequeños\n   ✅ 15 sacos disponibles\n\n¿Qué edad tiene tu perrito? 🦴",
  "tenant_slug": "mundo-canino",
  "tenant_name": "Mundo Canino Store"
}
```

**🎯 Nota importante**: Cada webhook procesa **SOLO** los productos y configuración de su tenant específico. ¡No hay mezcla de datos!

### Ejemplo 2: Crear Orden de Compra

```python
# Flujo de compra completo
mensajes = [
    {"mensaje": "Hola"},
    {"mensaje": "Quiero comprar Northern Lights"},
    {"mensaje": "2 unidades"},
    {"mensaje": "Mi nombre es Juan Pérez"},
    {"mensaje": "Confirmo la compra"}
]

for msg in mensajes:
    response = requests.post(
        "http://localhost:9001/webhook/acme",
        json={
            "telefono": "+56912345678",
            "mensaje": msg["mensaje"]
        }
    )
    print(f"Usuario: {msg['mensaje']}")
    print(f"Bot: {response.json()['respuesta']}\n")
```

### Ejemplo 3: Configuración de Prompt Personalizado

```python
import requests

# Configurar bot para ser más formal
config = {
    "system_prompt": """
    Eres un consultor experto en productos de cannabis medicinal.
    Debes ser extremadamente profesional y educativo.
    Siempre incluye información sobre beneficios medicinales.
    Usa terminología médica cuando sea apropiado.
    """,
    "style_overrides": {
        "tono": "profesional",
        "usar_emojis": False,
        "limite_respuesta_caracteres": 600,
        "cta_principal": "Consulte con su médico antes de usar"
    },
    "nlg_params": {
        "temperatura_nlg": 0.3,  # Más conservador
        "max_tokens_nlg": 400
    }
}

response = requests.put(
    "http://localhost:8000/api/tenants/acme-cannabis-2024/prompt",
    json=config,
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
```

### Ejemplo 4: Integración con Meta WhatsApp

```javascript
// Configurar webhook en Meta
const webhookConfig = {
    callback_url: "https://tudominio.com/webhook/meta",
    verify_token: "tu_token_verificacion",
    fields: ["messages", "messaging_postbacks"],
    include_values: true
};

// Verificar webhook
fetch(`https://graph.facebook.com/v17.0/${PHONE_NUMBER_ID}/subscribed_apps`, {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${ACCESS_TOKEN}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(webhookConfig)
});
```

---

## 🧪 Testing y Debug

### Scripts de Testing

#### 1. Test de Conectividad
```python
# test_connectivity.py
import requests

def test_bot_health():
    """Test que el bot está funcionando"""
    response = requests.get("http://localhost:9001/health")
    assert response.status_code == 200
    print("✅ Bot está funcionando")

def test_tenant_webhook():
    """Test webhook de tenant"""
    response = requests.post(
        "http://localhost:9001/webhook/acme",
        json={"telefono": "+56900000000", "mensaje": "test"}
    )
    assert response.status_code == 200
    assert "respuesta" in response.json()
    print("✅ Webhook de tenant funciona")

if __name__ == "__main__":
    test_bot_health()
    test_tenant_webhook()
```

#### 2. Test de Flujo Completo
```python
# test_flow.py
import requests
import time

class BotTester:
    def __init__(self, tenant_slug):
        self.base_url = f"http://localhost:9001/webhook/{tenant_slug}"
        self.telefono = f"+569{int(time.time()) % 100000000}"
    
    def send_message(self, mensaje):
        response = requests.post(
            self.base_url,
            json={"telefono": self.telefono, "mensaje": mensaje}
        )
        return response.json()["respuesta"]
    
    def test_conversation_flow(self):
        # Test saludo
        resp = self.send_message("Hola")
        assert "bienvenido" in resp.lower()
        print(f"✅ Saludo: {resp[:50]}...")
        
        # Test catálogo
        resp = self.send_message("Ver productos")
        assert "$" in resp  # Debe incluir precios
        print(f"✅ Catálogo mostrado")
        
        # Test búsqueda
        resp = self.send_message("Busco aceites")
        assert "aceite" in resp.lower() or "no" in resp.lower()
        print(f"✅ Búsqueda funciona")

# Ejecutar tests
tester = BotTester("acme")
tester.test_conversation_flow()
```

### Debugging con Logs

```python
# Habilitar logs detallados en el bot
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# En el código:
logger.debug(f"Tenant ID: {tenant_id}")
logger.info(f"Procesando mensaje: {mensaje}")
logger.error(f"Error en GPT: {e}")
```

### Monitoreo con Docker

```bash
# Ver logs en tiempo real
docker-compose logs -f whatsapp-bot

# Ver logs con filtro
docker-compose logs whatsapp-bot | grep ERROR

# Estadísticas de contenedor
docker stats whatsapp-bot

# Inspeccionar contenedor
docker-compose exec whatsapp-bot bash
```

---

## 🔧 Troubleshooting

### Problemas Comunes y Soluciones

#### 1. **Error: "Tenant not found"**
```python
# Verificar que el tenant existe
SELECT * FROM tenant_clients WHERE slug = 'tu-slug';

# Crear tenant si no existe
INSERT INTO tenant_clients (id, name, slug) 
VALUES ('nuevo-id-2024', 'Nuevo Tenant', 'nuevo');
```

#### 2. **Error: "OpenAI API key not configured"**
```bash
# Verificar variable de entorno
echo $OPENAI_API_KEY

# Configurar en .env
OPENAI_API_KEY=sk-...

# Reiniciar servicio
docker-compose restart whatsapp-bot
```

#### 3. **Mensajes no llegan al bot**
```python
# Verificar webhook de Meta
curl -X GET "http://localhost:9001/webhook/meta?hub.mode=subscribe&hub.verify_token=TOKEN&hub.challenge=test"

# Verificar logs de webhook
docker-compose logs whatsapp-bot | grep webhook

# Test directo al endpoint
curl -X POST http://localhost:9001/webhook/acme \
  -H "Content-Type: application/json" \
  -d '{"telefono": "+56900000000", "mensaje": "test"}'
```

#### 4. **Respuestas lentas o timeout**
```python
# Verificar performance de GPT
import time
start = time.time()
response = gpt_generate_response(...)
print(f"Tiempo GPT: {time.time() - start}s")

# Optimizar queries de BD
# Añadir índices
CREATE INDEX idx_products_client_status 
ON products(client_id, status);

# Limitar productos en respuesta
LIMIT 10
```

#### 5. **Sesiones no se mantienen**
```sql
-- Verificar sesión en BD
SELECT * FROM flow_sesiones 
WHERE telefono = '+56912345678' 
AND tenant_id = 'acme-cannabis-2024';

-- Limpiar sesiones antiguas
DELETE FROM flow_sesiones 
WHERE last_message_at < NOW() - INTERVAL '24 hours';
```

### Logs de Debug Útiles

```python
# En gpt_reasoning_engine.py
print(f"🧠 Tenant: {self.tenant_id}")
print(f"📦 Productos cargados: {len(self.productos)}")
print(f"💬 Mensaje: {mensaje}")
print(f"🎯 Decisión GPT: {action_decision}")
print(f"✅ Respuesta: {response[:100]}")

# En flow_chat_service.py
print(f"📞 Teléfono: {telefono}")
print(f"🏢 Tenant: {tenant_id}")
print(f"💾 Sesión ID: {sesion.id if sesion else 'Nueva'}")
print(f"📝 Estado: {sesion.estado if sesion else 'INITIAL'}")
```

### Comandos de Diagnóstico

```bash
# Estado del sistema
docker-compose ps

# Uso de recursos
docker system df

# Verificar conectividad BD
docker-compose exec postgres pg_isready

# Test de red entre contenedores
docker-compose exec whatsapp-bot ping postgres

# Revisar configuración
docker-compose config

# Logs específicos con timestamp
docker-compose logs --timestamps --tail=100 whatsapp-bot
```

---

## 📊 Métricas y Monitoreo

### KPIs del Bot

```sql
-- Mensajes por tenant
SELECT 
    tenant_id,
    COUNT(*) as total_mensajes,
    COUNT(DISTINCT telefono) as usuarios_unicos
FROM flow_sesiones
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY tenant_id;

-- Productos más consultados
SELECT 
    p.name,
    p.client_id,
    COUNT(*) as menciones
FROM products p
JOIN message_logs ml ON ml.message LIKE '%' || p.name || '%'
WHERE ml.created_at > NOW() - INTERVAL '30 days'
GROUP BY p.id, p.name, p.client_id
ORDER BY menciones DESC;

-- Tasa de conversión
SELECT 
    tenant_id,
    COUNT(DISTINCT CASE WHEN estado = 'COMPLETED' THEN telefono END)::float / 
    COUNT(DISTINCT telefono) * 100 as conversion_rate
FROM flow_sesiones
GROUP BY tenant_id;
```

---

## 🚀 Mejores Prácticas

### 1. **Configuración de Prompts**
- Mantén prompts concisos y claros
- Usa ejemplos específicos del negocio
- Actualiza según feedback de usuarios

### 2. **Gestión de Productos**
- Mantén descripciones actualizadas
- Usa categorías consistentes
- Actualiza stock en tiempo real

### 3. **Seguridad**
- Nunca hardcodees tokens
- Usa variables de entorno
- Valida siempre tenant_id
- Encripta datos sensibles

### 4. **Performance**
- Usa cache para configuraciones
- Limita productos en respuestas
- Implementa paginación
- Optimiza queries con índices

### 5. **Mantenimiento**
- Backup diario de BD
- Logs con rotación
- Monitoreo de errores
- Actualización regular de dependencias

---

## 📞 Soporte y Contacto

### Recursos Adicionales
- **Documentación OpenAI**: https://platform.openai.com/docs
- **Meta WhatsApp API**: https://developers.facebook.com/docs/whatsapp
- **Twilio WhatsApp**: https://www.twilio.com/docs/whatsapp
- **FastAPI Docs**: https://fastapi.tiangolo.com

### Estructura del Equipo
- **Backend**: FastAPI + SQLAlchemy
- **IA**: OpenAI GPT-4o-mini
- **Frontend**: Next.js + React
- **DevOps**: Docker + PostgreSQL

---

## 📝 Licencia y Créditos

**Versión**: 3.0.0
**Última Actualización**: Octubre 2024
**Stack**: FastAPI + OpenAI + PostgreSQL + Docker

---

*Documentación generada para el sistema WhatsApp Multi-Tenant E-commerce Bot*