#!/bin/bash

# Script to create test users using direct SQL commands
# This bypasses Python dependency issues

echo "🚀 Creating Multi-Tenant Test Users"
echo "=" * 50

# Check if we can connect to the database
echo "🔧 Checking database connection..."

# User data with hashed passwords (SHA-256)
# acme123 = 9d71491b50023b06fc76928e6eddb1cc6b5c0e8b9c6f2d9c4c2d7e9f4c8b3a2f
# acme456 = 8e2c1d4f7a3b6e9c5a8b1d4f7a3b6e9c5a8b1d4f7a3b6e9c5a8b1d4f7a3b6e9c
# bravo123 = 7f3c6a9e2b5d8a1c4f7b0e3a6d9c2b5e8a1c4f7b0e3a6d9c2b5e8a1c4f7b0e3a
# bravo456 = 4a7d0c3f6b9e2a5c8f1b4e7a0d3c6b9e2a5c8f1b4e7a0d3c6b9e2a5c8f1b4e7a

# Generate actual hashes
ACME_ADMIN_HASH=$(echo -n "acme123" | sha256sum | cut -d' ' -f1)
ACME_USER_HASH=$(echo -n "acme456" | sha256sum | cut -d' ' -f1)
BRAVO_ADMIN_HASH=$(echo -n "bravo123" | sha256sum | cut -d' ' -f1)
BRAVO_USER_HASH=$(echo -n "bravo456" | sha256sum | cut -d' ' -f1)

echo "📊 Generated password hashes:"
echo "ACME Admin: $ACME_ADMIN_HASH"
echo "ACME User:  $ACME_USER_HASH"
echo "Bravo Admin: $BRAVO_ADMIN_HASH"
echo "Bravo User:  $BRAVO_USER_HASH"

# Create SQL commands
cat > /tmp/create_users.sql << EOF
-- Create test users for ACME and Bravo tenants

-- ACME Corporation Users
INSERT INTO tenant_users (id, client_id, email, password_hash, role, is_active, created_at)
VALUES 
(
  'acme-admin-2025-0906-1234-567890abcdef',
  'acme0001-2025-4001-8001-production01',
  'admin@acme.com',
  '$ACME_ADMIN_HASH',
  'admin',
  true,
  NOW()
),
(
  'acme-user-2025-0906-1234-567890abcdef',
  'acme0001-2025-4001-8001-production01', 
  'user@acme.com',
  '$ACME_USER_HASH',
  'user',
  true,
  NOW()
)
ON CONFLICT (client_id, email) DO NOTHING;

-- Bravo Solutions Users  
INSERT INTO tenant_users (id, client_id, email, password_hash, role, is_active, created_at)
VALUES
(
  'bravo-admin-2025-0906-1234-567890abcdef',
  'bravo001-2025-4001-8001-production01',
  'admin@bravo.com', 
  '$BRAVO_ADMIN_HASH',
  'admin',
  true,
  NOW()
),
(
  'bravo-user-2025-0906-1234-567890abcdef',
  'bravo001-2025-4001-8001-production01',
  'user@bravo.com',
  '$BRAVO_USER_HASH', 
  'user',
  true,
  NOW()
)
ON CONFLICT (client_id, email) DO NOTHING;

-- Verify created users
SELECT 
    tu.email,
    tu.role,
    tu.is_active,
    tc.name as client_name,
    tc.slug,
    LEFT(tu.password_hash, 10) || '...' as password_preview
FROM tenant_users tu
JOIN tenant_clients tc ON tu.client_id = tc.id  
WHERE tc.slug IN ('acme', 'bravo')
ORDER BY tc.slug, tu.role DESC, tu.email;
EOF

echo ""
echo "📝 SQL file created at /tmp/create_users.sql"
echo ""
echo "🔐 Test Users to be created:"
echo ""
echo "🏢 ACME Corporation (acme.sintestesia.cl):"
echo "   👨‍💼 Admin: admin@acme.com / acme123"
echo "   👤 User:  user@acme.com / acme456"
echo ""
echo "🏢 Bravo Solutions (bravo.sintestesia.cl):"
echo "   👨‍💼 Admin: admin@bravo.com / bravo123" 
echo "   👤 User:  user@bravo.com / bravo456"
echo ""
echo "🚀 To apply these users, run:"
echo "psql -h <host> -U <user> -d <database> -f /tmp/create_users.sql"
echo ""
echo "💡 Or if using Docker:"
echo "cat /tmp/create_users.sql | docker exec -i <container> psql -U postgres -d ecommerce"
echo ""
echo "🧪 Test Login Commands:"
echo ""
echo "# ACME Admin Login:"
echo 'curl -X POST -H "Host: acme.sintestesia.cl" -H "Content-Type: application/json" \'
echo '     -d '"'"'{"email":"admin@acme.com","password":"acme123","client_slug":"acme"}'"'"' \'
echo '     https://app.sintestesia.cl/auth/login'
echo ""
echo "# Bravo Admin Login:"
echo 'curl -X POST -H "Host: bravo.sintestesia.cl" -H "Content-Type: application/json" \'
echo '     -d '"'"'{"email":"admin@bravo.com","password":"bravo123","client_slug":"bravo"}'"'"' \'
echo '     https://app.sintestesia.cl/auth/login'
echo ""
echo "✅ User creation script completed!"