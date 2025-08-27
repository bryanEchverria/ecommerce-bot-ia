# E-commerce Backoffice Docker Management
# Usage: make <command>

.PHONY: help build up down restart logs clean dev prod

# Default target
help:
	@echo "🐳 E-commerce Backoffice Docker Commands"
	@echo ""
	@echo "📦 Basic Commands:"
	@echo "  make build     - Build all containers"
	@echo "  make up        - Start all services"
	@echo "  make down      - Stop all services"
	@echo "  make restart   - Restart all services"
	@echo "  make logs      - Show logs for all services"
	@echo ""
	@echo "🔧 Development:"
	@echo "  make dev       - Start development environment"
	@echo "  make dev-logs  - Show development logs"
	@echo "  make dev-down  - Stop development environment"
	@echo ""
	@echo "🚀 Production:"
	@echo "  make prod      - Start production environment"
	@echo "  make prod-logs - Show production logs"
	@echo ""
	@echo "🗄️ Database:"
	@echo "  make db-shell  - Access PostgreSQL shell"
	@echo "  make db-backup - Create database backup"
	@echo "  make db-migrate- Run database migrations"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  make clean     - Remove containers and volumes"
	@echo "  make clean-all - Remove everything including images"
	@echo ""
	@echo "📊 Monitoring:"
	@echo "  make status    - Show container status"
	@echo "  make stats     - Show resource usage"

# Basic Commands
build:
	@echo "🔨 Building all containers..."
	docker-compose build

up:
	@echo "🚀 Starting all services..."
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "Frontend: http://localhost"
	@echo "Backend API: http://localhost:8002"
	@echo "API Docs: http://localhost:8002/docs"

down:
	@echo "⏹️ Stopping all services..."
	docker-compose down

restart:
	@echo "🔄 Restarting all services..."
	docker-compose restart

logs:
	@echo "📄 Showing logs for all services..."
	docker-compose logs -f

# Development Environment
dev:
	@echo "🔧 Starting development environment..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo "✅ Development environment started!"
	@echo "Backend: http://localhost:8003"
	@echo "Bot: http://localhost:9002"

dev-logs:
	@echo "📄 Showing development logs..."
	docker-compose -f docker-compose.dev.yml logs -f

dev-down:
	@echo "⏹️ Stopping development environment..."
	docker-compose -f docker-compose.dev.yml down

# Production Environment
prod: build up

prod-logs:
	@echo "📄 Showing production logs..."
	docker-compose logs -f --tail=100

# Database Operations
db-shell:
	@echo "🗄️ Accessing PostgreSQL shell..."
	docker-compose exec postgres psql -U postgres -d ecommerce

db-backup:
	@echo "💾 Creating database backup..."
	@mkdir -p backups
	docker-compose exec postgres pg_dump -U postgres ecommerce > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created in backups/ directory"

db-migrate:
	@echo "🔄 Running database migrations..."
	docker-compose exec backend alembic upgrade head

# Cleanup Commands
clean:
	@echo "🧹 Cleaning up containers and volumes..."
	docker-compose down -v
	docker container prune -f
	docker volume prune -f

clean-all: clean
	@echo "🧹 Removing all images..."
	docker image prune -a -f
	docker system prune -a -f

# Monitoring
status:
	@echo "📊 Container status:"
	docker-compose ps

stats:
	@echo "📈 Resource usage:"
	docker stats --no-stream

# Individual Service Commands
backend-logs:
	docker-compose logs -f backend

frontend-logs:
	docker-compose logs -f frontend

bot-logs:
	docker-compose logs -f whatsapp-bot

postgres-logs:
	docker-compose logs -f postgres

# Health Checks
health:
	@echo "🏥 Health check status:"
	@docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

# Environment Setup
setup-env:
	@echo "⚙️ Setting up environment..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "✅ .env file created from example"; else echo "⚠️ .env file already exists"; fi
	@echo "📝 Please edit .env file with your configuration"

# Quick Deploy
deploy: setup-env build up
	@echo "🎉 Deployment complete!"
	@echo "Please wait a moment for all services to start..."
	@sleep 10
	@make health

# Update Services
update:
	@echo "🔄 Updating services..."
	docker-compose pull
	docker-compose up -d
	@echo "✅ Services updated!"

# Test Services
test:
	@echo "🧪 Testing services..."
	@echo "Testing backend health..."
	@curl -f http://localhost:8002/health || echo "❌ Backend not healthy"
	@echo "Testing frontend..."
	@curl -f http://localhost/ || echo "❌ Frontend not accessible"
	@echo "✅ Basic tests completed"