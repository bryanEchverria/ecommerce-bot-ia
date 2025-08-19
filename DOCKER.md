# 🐳 Docker Deployment Guide

Guía completa para ejecutar el E-commerce Backoffice con Docker.

## 📋 Requisitos Previos

- Docker (v20.10+)
- Docker Compose (v2.0+)
- 4GB RAM disponible
- Puertos disponibles: 80, 5432, 6379, 8002, 9001

## 🚀 Inicio Rápido

### 1. Configurar Variables de Entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar las variables requeridas
nano .env
```

**Variables mínimas requeridas:**
```env
POSTGRES_PASSWORD=tu-password-seguro
SECRET_KEY=tu-clave-secreta-jwt
OPENAI_API_KEY=tu-openai-api-key
```

### 2. Levantar los Servicios

```bash
# Construcción y inicio completo
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Ver estado de servicios
docker-compose ps
```

### 3. Acceder a la Aplicación

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8002
- **API Docs**: http://localhost:8002/docs
- **WhatsApp Bot**: http://localhost:9001

## 🏗️ Arquitectura de Servicios

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │  WhatsApp Bot   │
│   (React)       │────│   (FastAPI)     │────│   (FastAPI)     │
│   Port: 80      │    │   Port: 8002    │    │   Port: 9001    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
              ┌─────────────────┐ │ ┌─────────────────┐
              │   PostgreSQL    │ │ │     Redis       │
              │   Port: 5432    │ │ │   Port: 6379    │
              └─────────────────┘   └─────────────────┘
```

## 📦 Servicios Incluidos

### 🎨 Frontend (Nginx + React)
- **Imagen**: Multi-stage build con Node.js 18 + Nginx Alpine
- **Puerto**: 80
- **Características**:
  - Build optimizado para producción
  - Gzip compression habilitado
  - Security headers configurados
  - Proxy reverso para API

### 🔧 Backend (FastAPI)
- **Imagen**: Python 3.11 slim
- **Puerto**: 8002
- **Características**:
  - Multi-tenant con PostgreSQL
  - Autenticación JWT
  - Documentación automática
  - Health checks

### 🤖 WhatsApp Bot (FastAPI + OpenAI)
- **Imagen**: Python 3.11 slim
- **Puerto**: 9001
- **Características**:
  - Integración OpenAI GPT
  - Contexto conversacional
  - Multi-tenant support
  - Webhook ready

### 🗄️ PostgreSQL
- **Imagen**: PostgreSQL 15 Alpine
- **Puerto**: 5432
- **Características**:
  - Datos persistentes
  - Configuración multi-tenant
  - Health checks
  - Inicialización automática

### 🚀 Redis (Opcional)
- **Imagen**: Redis 7 Alpine
- **Puerto**: 6379
- **Uso**: Cache y sesiones

## 🔧 Comandos Útiles

### Gestión de Contenedores
```bash
# Iniciar servicios
docker-compose up -d

# Parar servicios
docker-compose down

# Reiniciar un servicio específico
docker-compose restart backend

# Ver logs en tiempo real
docker-compose logs -f backend

# Ejecutar comandos en contenedor
docker-compose exec backend bash
```

### Base de Datos
```bash
# Acceder a PostgreSQL
docker-compose exec postgres psql -U postgres -d ecommerce

# Backup de base de datos
docker-compose exec postgres pg_dump -U postgres ecommerce > backup.sql

# Restaurar backup
docker-compose exec -T postgres psql -U postgres ecommerce < backup.sql

# Reset completo de datos
docker-compose down -v
docker-compose up -d
```

### Desarrollo
```bash
# Usar configuración de desarrollo
docker-compose -f docker-compose.dev.yml up -d

# Rebuilding después de cambios
docker-compose up -d --build backend

# Ver uso de recursos
docker stats
```

## 🌍 Configuración de Ambiente

### Producción
```env
ENVIRONMENT=production
POSTGRES_PASSWORD=password-muy-seguro
SECRET_KEY=clave-jwt-super-secreta
```

### Desarrollo
```env
ENVIRONMENT=development
# Se puede usar SQLite para desarrollo local
DATABASE_URL=sqlite:///./ecommerce.db
```

### Staging
```env
ENVIRONMENT=staging
# Configuración intermedia para testing
```

## 🔒 Seguridad

### Variables Sensibles
- Nunca commitear archivos `.env` con datos reales
- Usar `.env.example` como template
- Rotar keys de API regularmente

### Puertos de Red
```bash
# Solo exponer puertos necesarios en producción
ports:
  - "80:80"          # Frontend (público)
  - "8002:8002"      # Backend API (público)
  - "9001:9001"      # Bot Webhook (público)
  # PostgreSQL y Redis solo internos
```

### SSL/TLS
Para producción, usar reverse proxy (nginx/traefik) con SSL:
```yaml
# Ejemplo con Traefik
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.frontend.rule=Host(`tu-dominio.com`)"
  - "traefik.http.routers.frontend.tls.certresolver=letsencrypt"
```

## 📊 Monitoreo

### Health Checks
Todos los servicios incluyen health checks:
```bash
# Ver estado de salud
docker-compose ps

# Detalles de health check
docker inspect <container_name> | jq '.[0].State.Health'
```

### Logs
```bash
# Logs por servicio
docker-compose logs backend
docker-compose logs frontend
docker-compose logs whatsapp-bot

# Logs con timestamps
docker-compose logs -t -f
```

### Métricas
```bash
# Uso de recursos
docker stats

# Espacio en disco
docker system df

# Cleanup
docker system prune -a
```

## 🔄 Actualizaciones

### Rolling Updates
```bash
# Actualizar un servicio sin downtime
docker-compose up -d --no-deps backend

# Actualizar imagen específica
docker-compose pull backend
docker-compose up -d backend
```

### Migraciones de BD
```bash
# Ejecutar migraciones Alembic
docker-compose exec backend alembic upgrade head

# Crear nueva migración
docker-compose exec backend alembic revision --autogenerate -m "descripcion"
```

## 🐛 Troubleshooting

### Problemas Comunes

**Error: Puerto en uso**
```bash
# Verificar puertos ocupados
netstat -tulpn | grep :80
netstat -tulpn | grep :8002

# Cambiar puertos en docker-compose.yml
ports:
  - "8080:80"    # En lugar de 80:80
```

**Error: Base de datos no conecta**
```bash
# Verificar que PostgreSQL esté levantado
docker-compose ps postgres

# Ver logs de PostgreSQL
docker-compose logs postgres

# Verificar variables de entorno
docker-compose exec backend env | grep DATABASE
```

**Error: Out of memory**
```bash
# Verificar uso de memoria
docker stats

# Aumentar límites
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 512M
```

**Error: Permisos de archivos**
```bash
# En sistemas Linux/Mac, corregir ownership
sudo chown -R $USER:$USER .

# En Windows con WSL2
wsl --shutdown
wsl
```

### Debug Avanzado

**Acceder a contenedores**
```bash
# Shell interactivo
docker-compose exec backend bash
docker-compose exec postgres psql -U postgres

# Ejecutar comando único
docker-compose exec backend python -c "import sys; print(sys.path)"
```

**Network debugging**
```bash
# Ver redes Docker
docker network ls

# Inspeccionar red del proyecto
docker network inspect <project>_ecommerce-network

# Test conectividad entre servicios
docker-compose exec backend ping postgres
```

## 🚀 Deployment en Producción

### 1. Servidor Preparation
```bash
# Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
```

### 2. Environment Setup
```bash
# Clone repository
git clone <your-repo>
cd e-commerce-backoffice

# Setup environment
cp .env.example .env
# Edit .env with production values
```

### 3. Deploy
```bash
# Production deployment
docker-compose -f docker-compose.yml up -d

# Setup reverse proxy (nginx/traefik)
# Configure SSL certificates
# Setup monitoring (Prometheus/Grafana)
```

## 📈 Scaling

### Horizontal Scaling
```yaml
# docker-compose.override.yml
services:
  backend:
    deploy:
      replicas: 3
  
  whatsapp-bot:
    deploy:
      replicas: 2
```

### Load Balancing
Usar nginx o traefik como load balancer:
```yaml
# nginx.conf
upstream backend {
    server backend_1:8002;
    server backend_2:8002;
    server backend_3:8002;
}
```

## 🆘 Soporte

Si encuentras problemas:
1. Revisar logs: `docker-compose logs -f`
2. Verificar health checks: `docker-compose ps`
3. Revisar variables de entorno: `.env`
4. Consultar esta documentación
5. Crear issue en el repositorio

---

**✅ Sistema dockerizado completamente funcional con:**
- Multi-tenant architecture
- Production-ready containers
- Health checks y monitoring
- Security best practices
- Comprehensive documentation