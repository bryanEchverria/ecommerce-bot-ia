# Ecommerce Platform con Bot de WhatsApp

Plataforma completa de e-commerce con bot inteligente de WhatsApp para automatización de ventas.

## Estructura del Proyecto

```
ecommerce-platform/
├── ecommerce-bot-ia/           # Sistema principal
│   ├── backend/                # API del backoffice
│   ├── frontend/               # Interface web React
│   ├── whatsapp-bot-fastapi/   # Bot de WhatsApp
│   └── postgres-data/          # Base de datos
├── scripts/                    # Scripts organizados
│   ├── setup/                  # Configuración inicial
│   ├── testing/                # Scripts de pruebas
│   └── maintenance/            # Mantenimiento
├── docs/                       # Documentación completa
├── deployment/                 # Archivos de deployment
└── legacy/                     # Código obsoleto
```

## Componentes Principales

### 🏢 **Backend (API Backoffice)**
- **Ubicación**: `ecommerce-bot-ia/backend/`
- **Tecnología**: FastAPI + PostgreSQL
- **Funcionalidades**: 
  - Gestión multi-tenant
  - CRUD de productos, pedidos, clientes
  - Autenticación y autorización
  - Integración con WhatsApp (Twilio/Meta)

### 📱 **Bot de WhatsApp**
- **Ubicación**: `ecommerce-bot-ia/whatsapp-bot-fastapi/`
- **Tecnología**: FastAPI + IA (GPT)
- **Funcionalidades**:
  - Atención automatizada de clientes
  - Procesamiento de pedidos
  - Integración con catálogo
  - Soporte multi-provider (Twilio/Meta)

### 🖥️ **Frontend (Backoffice)**
- **Ubicación**: `ecommerce-bot-ia/frontend/`
- **Tecnología**: React + TypeScript + Vite
- **Funcionalidades**:
  - Panel de administración
  - Gestión de productos y pedidos
  - Dashboard de métricas
  - Configuración de WhatsApp

## Scripts de Utilidad

### 🔧 **Setup**
```bash
./scripts/setup/setup_production.sh      # Configuración de producción
./scripts/setup/configure_twilio_webhook.py  # Configurar Twilio
./scripts/setup/configure_meta_webhook.py     # Configurar Meta
```

### 🧪 **Testing** 
```bash
./scripts/testing/test_flujo_completo.py  # Prueba flujo completo
./scripts/testing/flow_smoke.sh          # Smoke tests
./scripts/testing/test_ai_improvements.py # Pruebas de IA
```

### 🔧 **Maintenance**
```bash
./scripts/maintenance/check_production.sh    # Verificar producción
./scripts/maintenance/monitor_twilio.sh      # Monitoreo Twilio
./scripts/maintenance/verify_backoffice.sh   # Verificar backoffice
```

## Inicio Rápido

1. **Configurar entorno**:
   ```bash
   cd ecommerce-platform/ecommerce-bot-ia
   docker-compose up -d
   ```

2. **Configurar webhooks**:
   ```bash
   python ../scripts/setup/configure_twilio_webhook.py
   ```

3. **Ejecutar pruebas**:
   ```bash
   ../scripts/testing/flow_smoke.sh
   ```

## Documentación Detallada

Ver archivos en `/docs/` para:
- Guías de deployment
- Configuración de WhatsApp
- Arquitectura multi-tenant
- Mejoras de IA implementadas

## Estado del Proyecto

✅ **Completado**: Reorganización y estructura
🔄 **En desarrollo**: Mejoras de IA y funcionalidades
📋 **Próximo**: Optimizaciones y nuevas features