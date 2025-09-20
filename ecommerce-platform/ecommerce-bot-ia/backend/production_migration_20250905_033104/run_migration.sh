#!/bin/bash
# Production Migration Execution Script
# Generated: 2025-09-05T03:31:04.567419

set -e  # Exit on any error

echo "🚀 Starting tenant_id migration for production"
echo "Time: $(date)"

# Pre-flight checks
echo "1️⃣ Running pre-flight checks..."
python3 4_check_schema.py

echo "2️⃣ Creating database backup..."
# Uncomment and configure for your production setup:
# pg_dump -h [PROD_HOST] -U [USER] -d ecommerce > backup_pre_tenant_migration_$(date +%Y%m%d_%H%M%S).sql

echo "3️⃣ Applying migration..."
python3 2_apply_migration.py

echo "4️⃣ Verifying migration..."
python3 3_verify_migration.py

echo "✅ Migration completed successfully!"
echo "Time: $(date)"

echo ""
echo "Next steps:"
echo "- Restart application services"
echo "- Run health checks"
echo "- Monitor logs for tenant_id related issues"
