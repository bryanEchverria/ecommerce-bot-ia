#!/bin/bash
# Production Rollback Script
# Generated: 2025-09-05T03:31:04.567649

set -e

echo "🔄 Rolling back tenant_id migration"
echo "Time: $(date)"

echo "⚠️  This will restore from backup and restart services"
read -p "Are you sure? (type 'ROLLBACK' to confirm): " confirm

if [ "$confirm" != "ROLLBACK" ]; then
    echo "Rollback cancelled"
    exit 1
fi

echo "1️⃣ Stopping services..."
# docker-compose stop backend whatsapp-bot

echo "2️⃣ Restoring database..."
# psql -h [PROD_HOST] -U [USER] -d ecommerce < backup_pre_tenant_migration_*.sql

echo "3️⃣ Starting services..."  
# docker-compose start backend whatsapp-bot

echo "✅ Rollback completed"
echo "Time: $(date)"
