#!/usr/bin/env python3
"""
Script to create test users for ACME and Bravo tenants
"""
import sys
import os
import hashlib
import uuid
from datetime import datetime

# Add backend to path
sys.path.append('/root/ecommerce-bot-ia/backend')

try:
    from database import SessionLocal
    from sqlalchemy import text
    import sqlalchemy as sa
except ImportError as e:
    print(f"❌ Error importing database modules: {e}")
    print("Make sure to install requirements first:")
    print("cd /root/ecommerce-bot-ia/backend && pip install -r requirements.txt")
    sys.exit(1)

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_users():
    """Create test users for ACME and Bravo tenants"""
    
    print("🔧 Creating test users for multi-tenant authentication...")
    
    # User data
    users_data = [
        # ACME Corporation Users
        {
            'client_id': 'acme0001-2025-4001-8001-production01',
            'client_name': 'ACME Corporation',
            'email': 'admin@acme.com',
            'password': 'acme123',
            'role': 'admin'
        },
        {
            'client_id': 'acme0001-2025-4001-8001-production01', 
            'client_name': 'ACME Corporation',
            'email': 'user@acme.com',
            'password': 'acme456',
            'role': 'user'
        },
        # Bravo Solutions Users
        {
            'client_id': 'bravo001-2025-4001-8001-production01',
            'client_name': 'Bravo Solutions', 
            'email': 'admin@bravo.com',
            'password': 'bravo123',
            'role': 'admin'
        },
        {
            'client_id': 'bravo001-2025-4001-8001-production01',
            'client_name': 'Bravo Solutions',
            'email': 'user@bravo.com', 
            'password': 'bravo456',
            'role': 'user'
        }
    ]
    
    try:
        with SessionLocal() as db:
            print("\n📊 Creating users in tenant_users table...")
            
            for user_data in users_data:
                # Check if user already exists
                existing = db.execute(
                    text("SELECT id FROM tenant_users WHERE client_id = :client_id AND email = :email"),
                    {"client_id": user_data['client_id'], "email": user_data['email']}
                ).fetchone()
                
                if existing:
                    print(f"⚠️  User {user_data['email']} already exists for {user_data['client_name']}")
                    continue
                
                # Generate user ID
                user_id = str(uuid.uuid4())
                
                # Hash password
                password_hash = hash_password(user_data['password'])
                
                # Insert user
                db.execute(
                    text("""
                    INSERT INTO tenant_users (id, client_id, email, password_hash, role, is_active, created_at)
                    VALUES (:id, :client_id, :email, :password_hash, :role, :is_active, :created_at)
                    """),
                    {
                        'id': user_id,
                        'client_id': user_data['client_id'],
                        'email': user_data['email'],
                        'password_hash': password_hash,
                        'role': user_data['role'],
                        'is_active': True,
                        'created_at': datetime.utcnow()
                    }
                )
                
                print(f"✅ Created {user_data['role']}: {user_data['email']} for {user_data['client_name']}")
            
            # Commit changes
            db.commit()
            
            print("\n📋 Users created successfully! Login credentials:")
            print("\n🏢 ACME Corporation (acme.sintestesia.cl):")
            print("   👨‍💼 Admin: admin@acme.com / acme123")
            print("   👤 User:  user@acme.com / acme456")
            
            print("\n🏢 Bravo Solutions (bravo.sintestesia.cl):")
            print("   👨‍💼 Admin: admin@bravo.com / bravo123") 
            print("   👤 User:  user@bravo.com / bravo456")
            
            print("\n🔐 Test Login Commands:")
            print("\n# ACME Admin Login:")
            print('curl -X POST -H "Host: acme.sintestesia.cl" -H "Content-Type: application/json" \\')
            print('     -d \'{"email":"admin@acme.com","password":"acme123","client_slug":"acme"}\' \\')
            print('     https://app.sintestesia.cl/auth/login')
            
            print("\n# Bravo Admin Login:")
            print('curl -X POST -H "Host: bravo.sintestesia.cl" -H "Content-Type: application/json" \\')
            print('     -d \'{"email":"admin@bravo.com","password":"bravo123","client_slug":"bravo"}\' \\')
            print('     https://app.sintestesia.cl/auth/login')
            
    except Exception as e:
        print(f"❌ Error creating users: {e}")
        return False
    
    return True

def verify_users():
    """Verify created users"""
    print("\n🧪 Verifying created users...")
    
    try:
        with SessionLocal() as db:
            result = db.execute(text("""
                SELECT 
                    tu.email,
                    tu.role,
                    tu.is_active,
                    tc.name as client_name,
                    tc.slug
                FROM tenant_users tu
                JOIN tenant_clients tc ON tu.client_id = tc.id
                WHERE tc.slug IN ('acme', 'bravo')
                ORDER BY tc.slug, tu.role DESC, tu.email
            """)).fetchall()
            
            if not result:
                print("❌ No users found")
                return False
                
            print("\n📊 Created Users Summary:")
            current_client = None
            for row in result:
                if current_client != row.slug:
                    current_client = row.slug
                    print(f"\n🏢 {row.client_name} ({row.slug}):")
                
                status = "✅ Active" if row.is_active else "❌ Inactive"
                print(f"   {row.role.title()}: {row.email} - {status}")
                
            return True
            
    except Exception as e:
        print(f"❌ Error verifying users: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Multi-Tenant User Creation Script")
    print("=" * 50)
    
    success = create_users()
    if success:
        verify_users()
        print("\n🎉 Test users created successfully!")
        print("\nYou can now test authentication with the provided credentials.")
    else:
        print("\n❌ Failed to create users")
        sys.exit(1)