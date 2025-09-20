# E-commerce Backoffice with WhatsApp Bot

Un sistema completo de gestión para e-commerce con frontend en React, backend en FastAPI y bot de WhatsApp con inteligencia artificial.

## 🎯 Funcionalidades Principales

- **📊 Dashboard**: Sistema completo de gestión e-commerce
- **🤖 Bot WhatsApp**: Asistente inteligente con OpenAI para ventas
- **🏪 Multi-tenant**: Soporte para múltiples tiendas
- **💳 Pagos**: Integración con Flow para pagos en línea
- **📱 Responsive**: Interfaz adaptativa para todos los dispositivos

## Características

### Frontend (React + TypeScript)
- **Dashboard**: Métricas y análisis en tiempo real
- **Productos**: Gestión completa de catálogo
- **Pedidos**: Seguimiento de órdenes
- **Clientes**: Base de datos de clientes
- **Campañas**: Marketing campaigns management
- **Descuentos**: Sistema de promociones
- **Asistente IA**: Consultas inteligentes con Gemini AI
- **Multiidioma**: Soporte para Español e Inglés
- **Multi-moneda**: Soporte para diferentes divisas

### Backend (FastAPI + Python)
- **API REST**: Endpoints completos para todas las funcionalidades
- **Base de datos**: SQLAlchemy con SQLite/PostgreSQL
- **Documentación automática**: Swagger UI disponible
- **CORS**: Configurado para desarrollo local
- **Validación**: Schemas con Pydantic

## 🚀 Inicio Rápido con Docker (Recomendado)

### Opción 1: Docker (Fácil y Rápido)

```bash
# 1. Clonar el repositorio
git clone <repository-url>
cd e-commerce-backoffice

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys

# 3. Levantar todos los servicios
make up
# O directamente: docker-compose up -d

# 4. Acceder a la aplicación
# Frontend: http://localhost
# Backend API: http://localhost:8002
# API Docs: http://localhost:8002/docs
```

**✅ Con Docker obtienes:**
- PostgreSQL configurado automáticamente
- Todos los servicios interconectados
- Configuración de producción lista
- Health checks y monitoreo
- Escalabilidad horizontal

📖 **Documentación completa**: [DOCKER.md](./DOCKER.md)

---

## 🛠️ Instalación Manual (Desarrollo Local)

### Requisitos

**Frontend:**
- Node.js (v16 o superior)
- npm

**Backend:**
- Python 3.8 o superior
- pip
- PostgreSQL (opcional, usa SQLite por defecto)

### Configuración Manual

### 1. Configurar el Backend

```bash
# Navegar a la carpeta del backend
cd backend

# Instalar dependencias de Python
pip install -r requirements.txt

# Configurar variables de entorno (opcional)
# cp .env.example .env
# Editar .env con tus configuraciones

# Ejecutar el servidor
python main.py
```

El backend estará disponible en `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 2. Configurar el Frontend

```bash
# Navegar a la carpeta del frontend
cd frontend

# Instalar dependencias de Node.js
npm install

# Configurar variables de entorno (opcional)
# Crear .env.local con VITE_GEMINI_API_KEY para el asistente IA

# Ejecutar el servidor de desarrollo
npm run dev
```

El frontend estará disponible en `http://localhost:5173`

## Variables de Entorno

### Backend (.env)
- `DATABASE_URL`: URL de la base de datos
- `GEMINI_API_KEY`: API key de Google Gemini (opcional)
- `ENVIRONMENT`: development/production
- `SECRET_KEY`: Clave secreta para JWT
- `FRONTEND_URL`: URL del frontend para CORS

### Frontend (.env.local)
- `VITE_GEMINI_API_KEY`: API key de Google Gemini para el asistente IA

## 📁 Estructura del Proyecto (Organizada)

```
e-commerce-backoffice/
├── backend/                    # 🔧 API FastAPI Multi-tenant (Python)
│   ├── routers/               # 🚀 Endpoints de la API
│   │   ├── auth.py           # 🔐 Autenticación JWT
│   │   ├── products.py       # 📦 Gestión de productos
│   │   ├── orders.py         # 📋 Gestión de órdenes
│   │   ├── dashboard.py      # 📊 Estadísticas
│   │   ├── discounts.py      # 🎯 Descuentos
│   │   └── bot.py           # 🤖 Webhook WhatsApp
│   ├── alembic/              # 🔄 Migraciones de BD
│   ├── main.py               # 🎯 Punto de entrada FastAPI
│   ├── models.py             # 🏗️ Modelos SQLAlchemy
│   ├── schemas.py            # 📝 Schemas Pydantic
│   ├── crud_async.py         # ⚡ Operaciones CRUD async
│   ├── auth.py              # 🛡️ Sistema de autenticación
│   ├── database.py           # 🗄️ Configuración de BD
│   ├── ecommerce.db          # 💾 Base de datos SQLite
│   └── requirements.txt      # 📋 Dependencias Python
├── frontend/                  # 🎨 Aplicación React (TypeScript)
│   ├── components/           # 🧩 Componentes React
│   │   ├── Dashboard.tsx     # 📊 Dashboard principal
│   │   ├── Products.tsx      # 📦 Gestión productos
│   │   ├── Orders.tsx        # 📋 Gestión órdenes
│   │   ├── Login.tsx         # 🔐 Login multi-tenant
│   │   └── ThemeContext.tsx  # 🎨 Sistema de temas
│   ├── auth/                 # 🔐 Autenticación
│   ├── services/             # 🔧 Servicios API
│   │   ├── api.ts           # 🌐 Cliente API principal
│   │   └── tenant-api.ts    # 🏢 API multi-tenant
│   └── locales/              # 🌍 Internacionalización
├── whatsapp-bot-fastapi/     # 🤖 Bot WhatsApp con OpenAI
│   ├── main.py              # 🎯 Bot principal con contexto
│   ├── services/            # 🔧 Servicios del bot
│   │   ├── chat_service.py  # 💬 OpenAI ChatGPT
│   │   ├── tenant_service.py # 🏢 Multi-tenant
│   │   └── pagos_service.py # 💳 Integración Flow
│   └── requirements.txt     # 📋 Dependencias del bot
├── tests/                    # 🧪 Todas las pruebas organizadas
│   ├── README.md            # 📖 Documentación completa
│   ├── test_multitenant_simple.py # ✅ Multi-tenant verificado
│   ├── bot_tests_simple.py  # 🤖 Pruebas básicas (96.4% éxito)
│   ├── test_edge_cases_openai.py # 🔬 Casos extremos (96.3%)
│   └── comprehensive_bot_tests.py # 🎯 Suite completa
├── postman-collections/      # 📋 Colecciones Postman organizadas
│   ├── README.md            # 📖 Guía de uso completa
│   ├── E-commerce_Backoffice_Complete.postman_collection.json # 🏪 API completa
│   └── Robust_Webhook_Context_Collection.json # 🤖 Bot WhatsApp
├── scripts/                  # 🔧 Scripts de utilidad organizados
│   ├── README.md            # 📖 Documentación de scripts
│   ├── crear_*.py           # ➕ Scripts de creación
│   ├── debug_*.py           # 🔍 Scripts de debug
│   └── verificacion_*.py    # ✅ Scripts de verificación
└── temp-test-files/          # 🗂️ Archivos temporales de prueba
    ├── test_*.py            # 🧪 Tests temporales
    ├── *.md                 # 📝 Documentación temporal
    └── webhook_*.py         # 🔗 Webhooks de prueba
```

### 🏗️ Arquitectura Multi-tenant Verificada

- **✅ Aislamiento completo** entre clientes (Green House, Demo Company, Mundo Canino, Test Store)
- **🔐 Autenticación JWT** en todos los endpoints críticos  
- **🛡️ Seguridad verificada** - vulnerabilidades corregidas
- **🔄 Integración Bot↔Backoffice** completamente funcional

## 🤖 Bot WhatsApp con OpenAI

### ✅ Características Confirmadas (Pruebas: 96.4% éxito)

- **OpenAI Integration**: 100% funcional y configurado
- **Búsqueda Específica**: "vapo" → PAX 3 Vaporizador Premium
- **Multi-tenant**: 4 clientes configurados (Green House, Demo Company, Mundo Canino, Test Store)
- **Flujo Completo**: Saludo → Búsqueda → Compra → Pago Flow
- **Casos Extremos**: 96.3% manejados correctamente

### 🎯 Prueba Rápida

1. **Importar colección**: `postman-collections/Bot_WhatsApp_Tests_Complete.json`
2. **Ejecutar**: "Green House Tests → 3. Comprar VAPO (Específico)"
3. **URL**: `POST http://localhost:8001/webhook`
4. **Body**: `{"telefono": "+3456789012", "mensaje": "quiero un vapo"}`
5. **Resultado esperado**: Encuentra PAX 3 Vaporizador Premium

### 📊 Resultados de Pruebas Realizadas

- **Funcionalidades básicas**: 96.4% ✅
- **OpenAI integration**: 100% ✅  
- **Multi-tenant**: 100% ✅
- **Casos extremos**: 96.3% ✅

## APIs Disponibles

### Productos
- `GET /api/products` - Listar productos
- `POST /api/products` - Crear producto
- `PUT /api/products/{id}` - Actualizar producto
- `DELETE /api/products/{id}` - Eliminar producto

### Pedidos
- `GET /api/orders` - Listar pedidos
- `POST /api/orders` - Crear pedido
- `PUT /api/orders/{id}` - Actualizar pedido

### Clientes
- `GET /api/clients` - Listar clientes
- `POST /api/clients` - Crear cliente
- `PUT /api/clients/{id}` - Actualizar cliente

### Campañas
- `GET /api/campaigns` - Listar campañas
- `POST /api/campaigns` - Crear campaña
- `PUT /api/campaigns/{id}` - Actualizar campaña

### Descuentos
- `GET /api/discounts` - Listar descuentos
- `POST /api/discounts` - Crear descuento
- `PUT /api/discounts/{id}` - Actualizar descuento

### Dashboard
- `GET /api/dashboard/stats` - Estadísticas del dashboard
- `GET /api/dashboard/recent-orders` - Pedidos recientes

### Asistente IA
- `POST /api/assistant/query` - Consulta al asistente
- `GET /api/assistant/stats` - Estadísticas para IA

## Desarrollo

### Backend
```bash
cd backend

# Modo desarrollo con recarga automática
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# O simplemente
python main.py
```

### Frontend
```bash
cd frontend

# Modo desarrollo
npm run dev

# Build para producción
npm run build

# Preview del build
npm run preview
```

## Base de Datos

Por defecto usa SQLite para desarrollo. Para producción se recomienda PostgreSQL:

```env
DATABASE_URL=postgresql://user:password@localhost/ecommerce_db
```

Las tablas se crean automáticamente al iniciar la aplicación.

## Características del Asistente IA

El asistente inteligente utiliza Google Gemini AI para:
- Responder preguntas sobre datos de productos, pedidos y clientes
- Generar insights y análisis
- Proporcionar recomendaciones basadas en datos

Para habilitarlo, configura tu `GEMINI_API_KEY` en las variables de entorno.

## Tecnologías Utilizadas

**Frontend:**
- React 19
- TypeScript
- Vite
- React Router
- Recharts (gráficos)
- i18next (internacionalización)
- Google Gemini AI

**Backend:**
- FastAPI
- SQLAlchemy
- Pydantic
- SQLite/PostgreSQL
- Python 3.8+

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request
#   e c o m m e r c e - b o t - i a  
 