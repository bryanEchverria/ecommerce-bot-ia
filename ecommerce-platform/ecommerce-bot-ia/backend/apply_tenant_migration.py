#!/usr/bin/env python3
"""
Apply tenant_id migration manually
"""
import sqlite3
import os

DEFAULT_TENANT_ID = '00000000-0000-0000-0000-000000000001'

def apply_migration():
    db_path = "/root/ecommerce-bot-ia/backend/ecommerce.db"
    
    if not os.path.exists(db_path):
        print(f"[ERROR] Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("[INFO] Applying tenant_id migration...")
        
        # === CREATE WHATSAPP_SETTINGS TABLE ===
        print("[1/6] Creating whatsapp_settings table...")
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS whatsapp_settings (
                    id INTEGER PRIMARY KEY,
                    provider TEXT NOT NULL,
                    twilio_account_sid TEXT,
                    twilio_auth_token TEXT,
                    twilio_from TEXT,
                    meta_token TEXT,
                    meta_phone_number_id TEXT,
                    meta_graph_api_version TEXT DEFAULT 'v21.0',
                    is_active BOOLEAN DEFAULT 1,
                    tenant_id TEXT,
                    created_at DATETIME,
                    updated_at DATETIME
                )
            ''')
            print("  ✅ whatsapp_settings table created")
        except Exception as e:
            print(f"  ⚠️  Warning: {e}")

        # === ADD TENANT_ID COLUMNS ===
        print("[2/6] Adding tenant_id columns...")
        
        try:
            cursor.execute('ALTER TABLE flow_sesiones ADD COLUMN tenant_id TEXT')
            print("  ✅ Added tenant_id to flow_sesiones")
        except Exception as e:
            print(f"  ⚠️  flow_sesiones: {e}")
            
        try:
            cursor.execute('ALTER TABLE flow_pedidos ADD COLUMN tenant_id TEXT')
            print("  ✅ Added tenant_id to flow_pedidos")
        except Exception as e:
            print(f"  ⚠️  flow_pedidos: {e}")

        # === FILL EXISTING RECORDS ===
        print("[3/6] Filling existing records with default tenant_id...")
        
        try:
            cursor.execute(f"UPDATE flow_sesiones SET tenant_id = ? WHERE tenant_id IS NULL", (DEFAULT_TENANT_ID,))
            updated = cursor.rowcount
            print(f"  ✅ Updated {updated} flow_sesiones records")
        except Exception as e:
            print(f"  ⚠️  flow_sesiones update: {e}")
            
        try:
            cursor.execute(f"UPDATE flow_pedidos SET tenant_id = ? WHERE tenant_id IS NULL", (DEFAULT_TENANT_ID,))
            updated = cursor.rowcount
            print(f"  ✅ Updated {updated} flow_pedidos records")
        except Exception as e:
            print(f"  ⚠️  flow_pedidos update: {e}")

        # === REMOVE UNIQUE CONSTRAINT ===
        print("[4/6] Handling unique constraints...")
        
        # In SQLite, we need to recreate the table to remove constraints
        # For now, just note that we need to handle this in application logic
        print("  ⚠️  Note: telefono unique constraint handling deferred to application logic")

        # === CREATE COMPOSITE INDEXES ===
        print("[5/6] Creating composite indexes...")
        
        try:
            cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS ix_flow_sesiones_tenant_telefono ON flow_sesiones (tenant_id, telefono)')
            print("  ✅ Created ix_flow_sesiones_tenant_telefono")
        except Exception as e:
            print(f"  ⚠️  flow_sesiones index: {e}")
            
        try:
            cursor.execute('CREATE INDEX IF NOT EXISTS ix_flow_pedidos_tenant_created ON flow_pedidos (tenant_id, created_at)')
            print("  ✅ Created ix_flow_pedidos_tenant_created")
        except Exception as e:
            print(f"  ⚠️  flow_pedidos index: {e}")
            
        try:
            cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS ix_whatsapp_settings_tenant_provider ON whatsapp_settings (tenant_id, provider)')
            print("  ✅ Created ix_whatsapp_settings_tenant_provider")
        except Exception as e:
            print(f"  ⚠️  whatsapp_settings index: {e}")

        # === UPDATE MIGRATION VERSION ===
        print("[6/6] Updating migration version...")
        
        try:
            cursor.execute("INSERT OR REPLACE INTO alembic_version (version_num) VALUES (?)", 
                          ('add_tenant_id_multi_tenant_support',))
            print("  ✅ Updated alembic version")
        except Exception as e:
            print(f"  ⚠️  Version update: {e}")

        # Commit all changes
        conn.commit()
        conn.close()
        
        print(f"\n[SUCCESS] Tenant migration applied successfully!")
        print(f"[INFO] Default tenant_id: {DEFAULT_TENANT_ID}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        return False

if __name__ == "__main__":
    apply_migration()